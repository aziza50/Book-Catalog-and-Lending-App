from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    """Custom User Admin Panel to Manage Patrons & Librarians"""
    model = User
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Roles & Permissions", {"fields": ("role", "is_staff", "is_superuser", "is_active")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role", "is_staff"),
        }),
    )

    search_fields = ("username", "email")
    ordering = ("username",)


# Register the custom user model
admin.site.register(User, CustomUserAdmin)
