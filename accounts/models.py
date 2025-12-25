from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import hashlib

class CustomUser(AbstractUser):
    middle_name = models.CharField(max_length=150, blank=True)
    
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_authorized = models.BooleanField(default=False)

    verification_code_hash = models.CharField(max_length=64, blank=True)
    verification_code_expires_at = models.DateTimeField(null=True, blank=True)

    def set_verification_code(self, code: str, minutes_valid: int = 10):
        self.verification_code_hash = hashlib.sha256(code.encode()).hexdigest()
        self.verification_code_expires_at = timezone.now() + timedelta(minutes=minutes_valid)

    def check_verification_code(self, code: str) -> bool:
        if not self.verification_code_expires_at:
            return False
        if timezone.now() > self.verification_code_expires_at:
            return False
        return hashlib.sha256(code.encode()).hexdigest() == self.verification_code_hash




def create_superuser(self, username, email=None, password=None, **extra_fields):
    extra_fields.setdefault("is_staff", True)
    extra_fields.setdefault("is_superuser", True)
    extra_fields.setdefault("is_admin", True)
    extra_fields.setdefault("is_authorized", True)  # ✅ auto authorize

    if not extra_fields.get("is_staff"):
        raise ValueError("Superuser must have is_staff=True.")
    if not extra_fields.get("is_superuser"):
        raise ValueError("Superuser must have is_superuser=True.")

    user = self.create_user(username=username, email=email, password=password, **extra_fields)
    return user
