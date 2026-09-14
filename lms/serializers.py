import re
from decimal import Decimal

from rest_framework import serializers

from lms.models import Course, Lesson, Subscription


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        # Интегрируем класс-валидатор в Meta

        # validators = [YoutubeOnlyValidator(field='video_url')]

    def validate_video_url(self, value):
        """Индивидуальная валидация поля video_url."""
        # Если поле не заполнено ( blank=True/null=True), пропускаем
        if not value:
            return value

        # Регулярное выражение
        youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'

        if not re.match(youtube_regex, value):
            raise serializers.ValidationError(
                "Разрешены ссылки только на видеохостинг youtube.com."
            )

        return value

class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    # Поле признака подписки текущего пользователя на курс
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'preview', 'description', 'lessons_count', 'is_subscribed', 'lessons')

    def get_lessons_count(self, obj):
        return obj.lessons.count() if obj.lessons else 0

    # Метод для проверки наличия подписки у текущего пользователя
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False

class SubscriptionRequestSerializer(serializers.Serializer):
    """Валидация входных данных для управления подпиской."""
    course_id = serializers.IntegerField(
        help_text="ID курса, на который пользователь хочет подписаться или отписаться."
    )


class SubscriptionResponseSerializer(serializers.Serializer):
    """Формат успешного ответа для Swagger."""
    message = serializers.CharField(help_text="Результат ('Подписка добавлена' или 'Подписка удалена').")


class CoursePaymentRequestSerializer(serializers.Serializer):
    """Валидация и описание параметров для создания платежа Stripe."""
    course_id = serializers.IntegerField(
        help_text="ID оплачиваемого курса."
    )
    # Используем DecimalField для безопасной работы с деньгами на уровне сериализатора
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        help_text="Сумма оплаты. Должна быть больше нуля (например, 499.90)."
    )


class CoursePaymentResponseSerializer(serializers.Serializer):
    """Формат ответа со ссылкой на оплату Stripe."""
    payment_url = serializers.URLField(help_text="Веб-ссылка на платежную страницу Stripe Checkout.")
    session_id = serializers.CharField(help_text="Уникальный ID сессии платежа в Stripe.")


class PaymentStatusResponseSerializer(serializers.Serializer):
    """Формат ответа проверки статуса."""
    status = serializers.CharField(help_text="Текущий статус оплаты из Stripe (например: 'paid', 'unpaid').")
