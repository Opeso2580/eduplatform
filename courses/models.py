from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone


class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    # ✅ admin approval switch
    is_approved = models.BooleanField(default=False)

    # optional tracking
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "course")

    def approve(self):
        self.is_approved = True
        self.approved_at = timezone.now()
        self.save(update_fields=["is_approved", "approved_at"])

    def __str__(self):
        status = "approved" if self.is_approved else "pending"
        return f"{self.student.username} -> {self.course.title} ({status})"
