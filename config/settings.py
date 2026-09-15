import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from celery import Celery

# Загружаем переменные из .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сторонние библиотеки
    'rest_framework',
    'drf_yasg',
    # Локальные приложения
    'users.apps.UsersConfig',
    'lms.apps.LmsConfig',
    # Фильтрация
    'django_filters',
     # JWT-авторизация
     'rest_framework_simplejwt',

     'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

# Новый формат настроек почты для Django 5.2+
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "HOST": "smtp.yandex.ru",
        "PORT": 465,
        "USE_TLS": False,
        "USE_SSL": True,
        "USER": "your_email@yandex.ru",
        "PASSWORD": os.getenv('EMAIL_PASSWORD'),  # Берем из .env
    }
}

DEFAULT_FROM_EMAIL = "your_email@yandex.ru"

# Базовый URL-адрес для доступа к медиафайлам через браузер
MEDIA_URL = '/media/'

# Абсолютный путь в файловой системе, где будут храниться загруженные файлы
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'users.User'

# Настройки JWT-токенов
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Все эндпоинты в проекте по умолчанию требуют авторизации
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


# Настройки срока действия токенов
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')

# Настройки для Celery
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'redis_protocol_version': 2
}
CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {
    'redis_protocol_version': 2
}

# URL-адрес брокера сообщений
CELERY_BROKER_URL = 'redis://localhost:6379/0'

# URL-адрес брокера результатов, также Redis
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Часовой пояс для работы Celery
CELERY_TIMEZONE = 'UTC'

# Обязательно включите поддержку часовых поясов
CELERY_ENABLE_UTC = True

# Флаг отслеживания выполнения задач
CELERY_TASK_TRACK_STARTED = True

# Максимальное время на выполнение задачи
CELERY_TASK_TIME_LIMIT = 30 * 60

# Настройки для Celery
CELERY_BEAT_SCHEDULE = {
    'block-inactive-users-every-day': {
        'task': 'users.tasks.check_inactive_users',  # Путь к задаче
        'schedule': timedelta(minutes=10),  # Расписание выполнения задачи (каждые 10 минут); (days=1) - 1 раз в день
    },
}
