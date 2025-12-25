from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Roles", {"fields": ("is_student", "is_teacher", "is_authorized")}),
    )
    list_display = ("username", "email", "is_student", "is_teacher", "is_staff", "is_superuser", "is_authorized")
    list_filter = ("is_student", "is_teacher", "is_staff", "is_superuser", "is_authorized")
