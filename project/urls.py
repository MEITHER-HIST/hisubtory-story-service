from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django_prometheus import exports

def health(request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    # 1. API 전용 경로
    path("api/stories/", include("stories.urls")),

    # 2. 시스템 및 모니터링
    path("metrics", exports.ExportToDjangoView, name="prometheus-metrics"),
    path("metrics/", exports.ExportToDjangoView),
    path("health/", health),
    path("", health),
    # path("api/library/", include("library.urls")),

    # 3. HTML/Legacy 경로 (기존 템플릿 페이지)
    # path("accounts/", include("accounts.urls")),
    path("stories/", include("stories.urls")),
    # path("library/", include("library.urls")),
    # path("", include("pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)