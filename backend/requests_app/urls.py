from django.urls import path
from .views import init_request, confirm_request, request_result, certificate_pdf

urlpatterns = [
    path("requests/init", init_request),
    path("requests/<int:request_id>/confirm", confirm_request),
    path("requests/<int:request_id>/result", request_result),
    path("requests/<int:request_id>/certificate.pdf", certificate_pdf),
]
