from django.contrib import admin
from .models import AdminUser, AdminAuditLog

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("username",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "admin", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("action", "admin__username")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
