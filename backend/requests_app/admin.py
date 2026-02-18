from django.contrib import admin
from .models import KraRequest
from payments.models import Payment

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    can_delete = False
    readonly_fields = ("method", "status", "amount", "till", "phone", "mpesa_receipt", "created_at")

@admin.register(KraRequest)
class KraRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "id_number", "first_name_input", "status", "created_at", "paid_at")
    list_filter = ("status", "created_at")
    search_fields = ("id_number", "first_name_input", "kra_full_name", "kra_pin", "mpesa_receipt")
    readonly_fields = ("created_at", "updated_at", "paid_at")
    ordering = ("-created_at",)
    inlines = [PaymentInline]
