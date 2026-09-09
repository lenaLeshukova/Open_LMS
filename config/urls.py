from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Open LMS API",
      default_version='v1',
      description="Документация для платформы онлайн-обучения Open LMS",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,), # Открыто для всех
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # урлы LMS
    path('api/', include('lms.urls', namespace='lms')),
    path('api/', include('users.urls', namespace='users')),

    # Эндпоинты документации
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
