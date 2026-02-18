from django.db import models

class AdminRole(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"

class AdminUser(models.Model):
    username = models.CharField(max_length=80, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=AdminRole.choices, default=AdminRole.ADMIN)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AdminAuditLog(models.Model):
    admin = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=120)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
