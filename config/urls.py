from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from study.views import health

urlpatterns = [
    path("health/", health),
    path("admin/", admin.site.urls),
    path("api/v1/", include("study.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    re_path(r"^(?!(?:api|admin|static|health)(?:/|$)).*$", TemplateView.as_view(template_name="index.html")),
]
