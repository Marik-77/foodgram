from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
else:
    _static_prefix = settings.STATIC_URL.strip('/')
    urlpatterns.insert(
        0,
        re_path(
            rf'^{_static_prefix}/(?P<path>.*)$',
            serve,
            {'document_root': str(settings.STATIC_ROOT)},
        ),
    )
