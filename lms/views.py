import re
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson, Subscription
from users.models import Payment
from lms.paginators import CustomPagination

from lms.permissions import IsModerator, IsOwner

from lms.serializers import (
    CourseSerializer,
    LessonSerializer,
    SubscriptionRequestSerializer,
    SubscriptionResponseSerializer,
    CoursePaymentRequestSerializer,
    CoursePaymentResponseSerializer,
    PaymentStatusResponseSerializer
)

from lms.services import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_checkout_session,
    retrieve_stripe_checkout_session
)


class CourseViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления курсами."""
    serializer_class = CourseSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='модераторы').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsOwner]
        return [permission() for permission in self.permission_classes]


class LessonListAPIView(generics.ListAPIView):
    """Просмотр списка уроков."""
    serializer_class = LessonSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonCreateAPIView(generics.CreateAPIView):
    """Создание нового урока."""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Детальный просмотр урока."""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Редактирование урока."""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока."""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]


# КАСТОВНЫЕ ЭНДПОИНТЫ (ПОДПИСКИ И СВЯЗКА СО STRIPE)

class SubscriptionAPIView(APIView):
    """Эндпоинт для управления подпиской пользователя на курс."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Переключает состояние подписки на курс (создает, если её нет, или удаляет, если она существует).",
        request_body=SubscriptionRequestSerializer,
        responses={200: SubscriptionResponseSerializer, 400: "Ошибка валидации", 404: "Курс не найден"}
    )
    def post(self, request, *args, **kwargs):
        # Валидируем входной параметр course_id через сериализатор
        serializer = SubscriptionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data['course_id']
        course_item = get_object_or_404(Course, id=course_id)

        subs_item = Subscription.objects.filter(user=request.user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка удалена'
        else:
            Subscription.objects.create(user=request.user, course=course_item)
            message = 'Подписка добавлена'

        return Response({"message": message}, status=status.HTTP_200_OK)


class CoursePaymentAPIView(APIView):
    """Эндпоинт для инициализации оплаты курса через Stripe."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Создает сессию оплаты в Stripe, сохраняет запись транзакции в БД и возвращает ссылку.",
        request_body=CoursePaymentRequestSerializer,
        responses={201: CoursePaymentResponseSerializer, 400: "Неверная сумма или данные курса"}
    )
    def post(self, request, *args, **kwargs):
        # Автоматическая валидация: проверяет, что course_id передан, а amount - число > 0
        serializer = CoursePaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data['course_id']
        amount = serializer.validated_data['amount']

        course = get_object_or_404(Course, id=course_id)

        try:
            # 1. Создаем продукт в Stripe
            product_id = create_stripe_product(name=course.title, description=f"Оплата курса: {course.title}")

            # 2. Создаем цену (внутри функции происходит безопасный перевод Decimal в центы)
            price_id = create_stripe_price(product_id=product_id, amount=amount)

            # 3. Создаем сессию оплаты и получаем рабочую ссылку
            payment_url, session_id = create_stripe_checkout_session(price_id=price_id)

            # 4. СОХРАНЯЕМ ПЛАТЕЖ В БАЗУ ДАННЫХ
            Payment.objects.create(
                user=request.user,
                paid_course=course,
                amount=amount,
                stripe_session_id=session_id,
                payment_link=payment_url,
                payment_status='pending'
            )

            return Response(
                {"payment_url": payment_url, "session_id": session_id},
                status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Ошибка платежной системы: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class PaymentStatusAPIView(APIView):
    """Эндпоинт для ручной проверки статуса платежа по ID сессии."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получает актуальный статус сессии из Stripe, обновляет БД и при успехе активирует подписку.",
        manual_parameters=[
            openapi.Parameter(
                'session_id',
                openapi.IN_QUERY,
                description="ID сессии Stripe (полученный при создании платежа)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: PaymentStatusResponseSerializer, 400: "Не передан параметр session_id или сессия не найдена"}
    )
    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get('session_id')

        if not session_id:
            return Response({"error": "Параметр session_id обязателен в query params."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Находим платеж у себя в БД по ID сессии Stripe
        payment = get_object_or_404(Payment, stripe_session_id=session_id)

        try:
            # Запрашиваем статус у Stripe API
            status_payment = retrieve_stripe_checkout_session(session_id)

            # Если Stripe подтверждает оплату, а у нас статус еще не 'paid'
            if status_payment == 'paid' and payment.payment_status != 'paid':
                # Обновляем статус платежа
                payment.payment_status = 'paid'
                payment.save()

                # АВТОМАТИЧЕСКАЯ АКТИВАЦИЯ ДОСТУПА/ПОДПИСКИ
                Subscription.objects.get_or_create(
                    user=payment.user,
                    course=payment.paid_course
                )

            return Response({"status": status_payment}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Не удалось получить статус: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
