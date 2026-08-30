import re
from rest_framework.serializers import ValidationError


class YoutubeOnlyValidator:
    """Валидатор проверяет, что ссылка ведет исключительно на youtube.com."""

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        url = value.get(self.field)

        # Если поле не заполнено, пропускаем (разрешено blank=True)
        if not url:
            return

        # Регулярное выражение для проверки домена youtube.com или youtu.be
        youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'

        if not re.match(youtube_regex, url):
            raise ValidationError(
                {self.field: "Разрешены ссылки только на видеохостинг youtube.com."}
            )
