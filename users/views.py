from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course
from lms.services import (
    create_stripe_product, create_stripe_price,
    create_stripe_checkout_session, retrieve_stripe_checkout_session
)
from users.models import Payment
from users.models import User
from users.serializers import PaymentSerializer
from users.serializers import UserSerializer


# Контролеры Пользователей
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)  # Регистрация доступна всем

class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

class UserDestroyAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

# Контролер Платежей
class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


    # Подключаем бэкенды фильтрации и сортировки
    filter_backends = (DjangoFilterBackend, OrderingFilter)

    # Настраиваем поля для точечной фильтрации
    filterset_fields = ('paid_course', 'paid_lesson', 'payment_method')

    # Настраиваем поля для сортировки (по дате)
    ordering_fields = ('payment_date',)
    permission_classes = (IsAuthenticated,)

class CoursePaymentAPIView(APIView):
    """Эндпоинт покупки курса через Stripe с сохранением ссылки в модель."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        amount = request.data.get('amount')

        if not course_id or not amount:
            return Response({"error": "Поля course_id и amount обязательны."}, status=400)

        course = get_object_or_404(Course, id=course_id)

        # 1. Сначала создаем черновик платежа в нашей системе PostgreSQL
        payment = Payment.objects.create(
            user=request.user,
            paid_course=course,
            amount=amount,
            payment_method='transfer',
            payment_status='pending'
        )

        try:
            # 2. Передаем данные из модели во внешний сервис Stripe
            stripe_product_id = create_stripe_product(name=course.title, description=course.description)
            stripe_price_id = create_stripe_price(product_id=stripe_product_id, amount=payment.amount)
            checkout_url, session_id = create_stripe_checkout_session(price_id=stripe_price_id)

            # 3. Сохраняем полученную ссылку и ID сессии Stripe в объект платежа по подсказке
            payment.payment_link = checkout_url
            payment.stripe_session_id = session_id
            payment.save()

            # 4. Отдаем пользователю полные данные о платеже (включая ссылку) через сериализатор
            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=201)

        except Exception as e:
            payment.payment_status = 'failed'
            payment.save()
            return Response({"error": str(e)}, status=500)


class PaymentStatusAPIView(APIView):
    """Дополнительный эндпоинт для синхронизации и проверки статуса платежа."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        # Ищем платеж в нашей системе по ID
        payment = get_object_or_404(Payment, id=pk, user=request.user)

        if not payment.stripe_session_id:
            return Response({"error": "Для данного платежа не найдена сессия Stripe."}, status=400)

        try:
            # Запрашиваем статус напрямую у Stripe API
            stripe_status = retrieve_stripe_checkout_session(payment.stripe_session_id)

            # Обновляем статус в нашей базе данных
            if stripe_status == 'paid':
                payment.payment_status = 'completed'
            elif stripe_status == 'unpaid':
                payment.payment_status = 'pending'
            payment.save()

            return Response({
                "payment_id": payment.id,
                "stripe_status": stripe_status,
                "internal_status": payment.payment_status
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)
