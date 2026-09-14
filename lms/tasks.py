from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from lms.models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    """Фоновая задача для отправки писем подписчикам с защитой от спама < 4 часов."""
    try:
        course = Course.objects.get(id=course_id)

        # Логика проверки времени (текущее время минус время обновления < 4 часов)
        # Так как задача выполняется асинхронно, мы проверяем, не было ли это изменение слишком частым
        now = timezone.now()
        if course.updated_at and (now - course.updated_at) > timedelta(hours=4):
            return f"Обновление курса '{course.title}' пропущено (прошло меньше 4 часов с прошлого уведомления)."

        subscriptions = Subscription.objects.filter(course=course)
        if not subscriptions.exists():
            return f"У курса '{course.title}' нет подписчиков."

        recipient_list = [sub.user.email for sub in subscriptions if sub.user.email]

        if recipient_list:
            send_mail(
                subject=f"Обновление курса: {course.title}",
                message=f"Здравствуйте! Материалы курса '{course.title}', на который вы подписаны, были обновлены.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return f"Уведомление отправлено {len(recipient_list)} пользователям."
    except Course.DoesNotExist:
        return f"Курс с ID {course_id} не найден."

