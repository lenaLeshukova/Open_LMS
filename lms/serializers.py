from rest_framework import serializers

from lms.models import Course, Lesson, Subscription
from lms.validators import YoutubeOnlyValidator
from rest_framework import serializers
from lms.models import Course, Lesson, Subscription
import re

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

