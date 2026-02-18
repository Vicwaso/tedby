from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "request", "method", "status", "amount", "till", "mpesa_receipt", "created_at")
    list_filter = ("method", "status", "created_at")
    search_fields = ("mpesa_receipt", "phone", "request__id_number", "request__kra_full_name")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
