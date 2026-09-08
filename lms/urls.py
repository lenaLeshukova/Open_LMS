from django.urls import path
from rest_framework.routers import DefaultRouter
from lms.apps import LmsConfig
from lms.views import (
    CourseViewSet,
    LessonListAPIView,
    LessonCreateAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
    SubscriptionAPIView,
    CoursePaymentAPIView,
    PaymentStatusAPIView
)

app_name = LmsConfig.name

# Регистрируем ViewSet для курсов
router = DefaultRouter()
router.register(prefix=r'courses', viewset=CourseViewSet, basename='courses')

urlpatterns = [
                  # Урлы для уроков (Generics)
                  path('lessons/', LessonListAPIView.as_view(), name='lesson-list'),
                  path('lessons/create/', LessonCreateAPIView.as_view(), name='lesson-create'),
                  path('lessons/<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson-get'),
                  path('lessons/update/<int:pk>/', LessonUpdateAPIView.as_view(), name='lesson-update'),
                  path('lessons/delete/<int:pk>/', LessonDestroyAPIView.as_view(), name='lesson-delete'),

                  # Подписки
                  path('subscription/', SubscriptionAPIView.as_view(), name='subscription'),

                  # Платежи
                  path('payments/create/', CoursePaymentAPIView.as_view(), name='payment-create'),
                  path('payments/status/', PaymentStatusAPIView.as_view(), name='payment-status'),
              ] + router.urls
