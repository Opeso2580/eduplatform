from django.contrib import admin
from .models import Course
from .models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "slug")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "is_approved", "requested_at", "approved_at")
    list_filter = ("is_approved", "course")
    search_fields = ("student__username", "student__email", "course__title")
    autocomplete_fields = ("student", "course")
    list_editable = ("is_approved",)