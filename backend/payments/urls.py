from django.urls import path
from .views import manual_verify, stk_push, payment_status, simulate_paid

urlpatterns = [
    path("payments/manual-verify", manual_verify),
    path("payments/stk-push", stk_push),
    path("payments/status/<int:request_id>", payment_status),
    path("payments/simulate-paid/<int:request_id>", simulate_paid),
]
