from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from lms.models import Course, Lesson, Subscription

User = get_user_model()


class LMSTestCase(APITestCase):

    def setUp(self):
        """Заполнение базы данных тестовыми данными перед каждым тестом."""
        # Создаем пользователей
        self.user = User.objects.create_user(email="student@test.com", password="password123")
        self.other_user = User.objects.create_user(email="other@test.com", password="password123")

        # Создаем тестовый курс для первого пользователя
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание курса",
            owner=self.user
        )

        # Создаем тестовый урок для первого пользователя
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Тестовый урок",
            description="Описание урока",
            video_url="https://youtube.com",
            owner=self.user
        )

    def test_lesson_create(self):
        """Тест создания урока авторизованным пользователем."""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-create")
        data = {
            "title": "Новый урок",
            "description": "Детали",
            "course": self.course.id,
            "video_url": "https://youtube.com/1"
        }
        response = self.client.post(url, data=data)

        # print("\n--- ОШИБКА В ТЕСТЕ СОЗДАНИЯ УРОКА ---", response.json())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_validation_error(self):
        """Тест валидатора ссылок (запрет сторонних ресурсов)."""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-create")
        data = {
            "title": "Урок с плохой ссылкой",
            "course": self.course.id,
            "video_url": "https://vimeo.com" # Сторонний ресурс
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_list(self):
        """Тест получения списка уроков владельца."""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Так как работает пагинация, данные лежат в ключе 'results'
        self.assertEqual(len(response.data['results']), 1)

    def test_lesson_retrieve(self):
        """Тест получения деталей урока владельцем."""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-get", kwargs={"pk": self.lesson.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.lesson.title)

    def test_lesson_retrieve_anonymous_or_wrong_user(self):
        """Тест ограничения доступа: другой пользователь не видит чужой урок."""
        self.client.force_authenticate(user=self.other_user)
        url = reverse("lms:lesson-get", kwargs={"pk": self.lesson.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update(self):
        """Тест обновления урока владельцем."""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-update", kwargs={"pk": self.lesson.pk})
        data = {"title": "Обновленное название"}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Обновленное название")

    def test_lesson_delete(self):
        """Тест удаления урока владельцем."""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:lesson-delete", kwargs={"pk": self.lesson.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_subscription_toggle(self):
        """Тест работы механизма подписки (активация и деактивация)."""
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:course-subscribe")
        data = {"course_id": self.course.id}

        # 1. Первый клик - создание подписки
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # 2. Повторный клик - удаление подписки
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.data["message"], ["Подписка deleted", "Подписка удалена"])
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())
