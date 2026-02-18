from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("requests_app.urls")),
    path("api/", include("payments.urls")),
]
