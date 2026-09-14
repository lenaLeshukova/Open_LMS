from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def check_inactive_users():
    """Периодическая задача: блокировка пользователей, не заходивших более месяца."""
    one_month_ago = timezone.now() - timedelta(days=30)

    # Ищем активных пользователей, у которых дата последнего входа старше 30 дней,
    # и исключаем суперпользователей, чтобы случайно не заблокировать админку
    inactive_users = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True,
        is_superuser=False
    )

    count = inactive_users.count()
    if count > 0:
        # Массово деактивируем флаг Is_active
        inactive_users.update(is_active=False)
        return f"Успешно заблокировано неактивных пользователей: {count}."

    return "Неактивных пользователей для блокировки не обнаружено."
