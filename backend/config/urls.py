from django.contrib import admin
from django.urls import path, include

from django.http import HttpResponse

def home(request):
    return HttpResponse("TEDBY API is running.")

urlpatterns = [
    path("", home),  # 👈 ADD THIS
    path("admin/", admin.site.urls),
    path("api/", include("requests_app.urls")),
    path("api/", include("payments.urls")),
]
