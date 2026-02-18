from django.db import models
from requests_app.models import KraRequest

class PaymentMethod(models.TextChoices):
    STK = "STK"
    MANUAL = "MANUAL"

class PaymentStatus(models.TextChoices):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    DUPLICATE = "DUPLICATE"

class Payment(models.Model):
    request = models.ForeignKey(KraRequest, on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    status = models.CharField(max_length=12, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)

    amount = models.PositiveIntegerField(default=100)
    till = models.CharField(max_length=20, default="8993804")

    phone = models.CharField(max_length=20, blank=True, default="")
    mpesa_receipt = models.CharField(max_length=20, blank=True, default="", unique=True)

    raw_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
