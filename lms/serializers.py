from rest_framework import serializers
from lms.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    # Поле для вывода количества уроков
    lessons_count = serializers.SerializerMethodField()

    # Поле для вывода деталей всех связанных уроков
    # related_name='lessons' в ForeignKey позволяет нам использовать это имя здесь
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'title', 'preview', 'description', 'lessons_count', 'lessons')

    # Метод для подсчета количества уроков (префикс get_ обязателен)
    def get_lessons_count(self, obj):
        return obj.lessons.count()

