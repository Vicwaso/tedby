from django.db import models

class RequestStatus(models.TextChoices):
    LOOKUP_OK = "LOOKUP_OK"
    CONFIRMED = "CONFIRMED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAID = "PAID"
    RELEASED = "RELEASED"

class KraRequest(models.Model):
    id_number = models.CharField(max_length=10)
    first_name_input = models.CharField(max_length=60)
    paid_at = models.DateTimeField(null=True, blank=True)

    kra_full_name = models.CharField(max_length=200, blank=True, default="")
    masked_name = models.CharField(max_length=200, blank=True, default="")
    kra_pin = models.CharField(max_length=20, blank=True, default="")

    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.LOOKUP_OK
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=80, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
