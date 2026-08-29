from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer

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
