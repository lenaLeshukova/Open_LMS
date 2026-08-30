from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson
from lms.models import Subscription
from lms.paginators import CustomPagination
from lms.permissions import IsModerator, IsOwner
from lms.serializers import CourseSerializer, LessonSerializer


# Контролеры для Курсов (Viewset)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    pagination_class = CustomPagination  # Интеграция пагинации

    def get_queryset(self):

        # Фильтрация списков по роли
        user = self.request.user
        if user.groups.filter(name='модераторы').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        # Автоматическая привязка владельца
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        # Настройка разрешений под каждый action отдельно
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsOwner]
        return [permission() for permission in self.permission_classes]


# Контролеры для Уроков (Generics)
class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    pagination_class = CustomPagination  # Интеграция пагинации

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]

class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]

class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class SubscriptionAPIView(APIView):
    """Эндпоинт для управления подпиской пользователя на курс."""
    permission_classes = [IsAuthenticated]  # Доступ только авторизованным

    def post(self, request, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get('course_id')

        # Получаем объект курса или отдаем 404
        course_item = get_object_or_404(Course, id=course_id)

        # Ищем существующую подписку
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            # Если подписка есть - удаляем её
            subs_item.delete()
            message = 'Подписка удалена'
        else:
            # Если подписки нет - создаем её
            Subscription.objects.create(user=user, course=course_item)
            message = 'Подписка добавлена'

        return Response({"message": message})
