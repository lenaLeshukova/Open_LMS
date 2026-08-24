from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from lms.models import Course, Lesson

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=35, verbose_name="Телефон", blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name="Город", blank=True, null=True)
    avatar = models.ImageField(upload_to="users/avatars/", verbose_name="Аватарка", blank=True, null=True)

    # Обязательные служебные поля для работы админки Django
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Сотрудник")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    CASH = 'cash'
    TRANSFER = 'transfer'

    PAYMENT_METHODS = [
        (CASH, 'Наличные'),
        (TRANSFER, 'Перевод на счет'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', verbose_name='Пользователь')
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты')

    # Ссылки на курс или урок (что-то одно будет заполнено)
    paid_course = models.ForeignKey('lms.Course', on_delete=models.SET_NULL, blank=True, null=True,
                                    verbose_name='Оплаченный курс')
    paid_lesson = models.ForeignKey('lms.Lesson', on_delete=models.SET_NULL, blank=True, null=True,
                                    verbose_name='Оплаченный урок')
    # DecimalField требует обязательного указания параметра max_digits (общее количество цифр)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма оплаты')
    #max_length используется только для текстовых полей (CharField)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default=TRANSFER,
                                      verbose_name='Способ оплаты')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f'{self.user} - {self.amount} ({self.payment_date})'
