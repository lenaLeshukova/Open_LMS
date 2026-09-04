from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import CoursePaymentAPIView
from users.views import (
    PaymentListAPIView, UserCreateAPIView, UserListAPIView,
    UserRetrieveAPIView, UserUpdateAPIView, UserDestroyAPIView
)
from users.views import CoursePaymentAPIView, PaymentStatusAPIView

app_name = UsersConfig.name

urlpatterns = [
    # Токены (Логин)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Пользователи
    path('users/register/', UserCreateAPIView.as_view(), name='user-register'),
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserRetrieveAPIView.as_view(), name='user-detail'),
    path('users/update/<int:pk>/', UserUpdateAPIView.as_view(), name='user-update'),
    path('users/delete/<int:pk>/', UserDestroyAPIView.as_view(), name='user-delete'),

    # Платежи
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('payments/create/', CoursePaymentAPIView.as_view(), name='payment-create'),
    path('payments/<int:pk>/status/', PaymentStatusAPIView.as_view(), name='payment-status'),
]
