import secrets
import logging
import socket

from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from .forms import StudentSignUpForm, VerifyCodeForm

User = get_user_model()
logger = logging.getLogger(__name__)


def safe_send_verification_email(user, code, subject):
    """
    Sends verification email without crashing the request.
    If email fails, we log the error + TEMP code so you can verify via Render logs.
    """
    message = (
        f"Hi {user.first_name or 'there'},\n\n"
        "Thank you for signing up for Vantage Lingua Hub! 🎉\n\n"
        "To complete your registration, please enter the 6-digit verification code below:\n\n"
        f"{code}\n\n"
        "This code expires in 10 minutes.\n\n"
        "If you did not create this account, you may safely ignore this email.\n\n"
        "Warm regards,\n"
        "Vantage Lingua Hub Team"
    )

    try:
        # Prevent long hangs that cause Gunicorn worker timeouts
        socket.setdefaulttimeout(10)

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True

    except Exception as e:
        logger.exception("Email send failed for %s: %s", getattr(user, "email", ""), e)
        logger.warning("TEMP VERIFY CODE for %s is: %s", getattr(user, "email", ""), code)
        return False


def student_login(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is None:
            error = "Invalid username or password."
        else:
            # ✅ Auto-authorize admins + send them to admin panel
            if user.is_superuser or user.is_staff:
                if hasattr(user, "is_authorized") and not getattr(user, "is_authorized", True):
                    user.is_authorized = True
                    user.save(update_fields=["is_authorized"])
                login(request, user)
                return redirect("/admin/")

            # ✅ Students: block login if not authorized
            if getattr(user, "is_student", False) and not getattr(user, "is_authorized", True):
                request.session["pending_user_id"] = user.id
                return redirect("student_verify")

            # ✅ Normal login
            login(request, user)
            return redirect("student_dashboard")

    return render(request, "accounts/student_login.html", {"error": error})


def student_signup(request):
    # optional: if already logged in, go dashboard
    if request.user.is_authenticated:
        return redirect("student_dashboard")

    form = StudentSignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)

        # ✅ Save names (first_name/last_name exist on AbstractUser)
        user.first_name = form.cleaned_data.get("first_name", "").strip()
        user.middle_name = form.cleaned_data.get("middle_name", "").strip()  # you added this field
        user.last_name = form.cleaned_data.get("last_name", "").strip()

        # ✅ email
        user.email = form.cleaned_data["email"].strip().lower()

        # ✅ mark student + not authorized until verified
        user.is_student = True
        user.is_authorized = False

        # ✅ set password and save
        user.set_password(form.cleaned_data["password1"])
        user.save()

        # ✅ generate and store code
        code = f"{secrets.randbelow(10**6):06d}"
        user.set_verification_code(code, minutes_valid=10)
        user.save()

        # ✅ send email (non-blocking; won't crash if SMTP fails)
        sent = safe_send_verification_email(
            user=user,
            code=code,
            subject="Welcome to Vantage Lingua Hub – Verify Your Account",
        )
        request.session["email_sent"] = sent

        request.session["pending_user_id"] = user.id
        return redirect("student_verify")

    return render(request, "accounts/student_signup.html", {"form": form})


def student_verify(request):
    pending_id = request.session.get("pending_user_id")
    if not pending_id:
        return redirect("student_login")

    user = User.objects.filter(id=pending_id).first()
    if not user:
        return redirect("student_login")

    form = VerifyCodeForm(request.POST or None)
    error = None

    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["code"].strip()

        if user.check_verification_code(code):
            user.is_authorized = True
            user.verification_code_hash = ""
            user.verification_code_expires_at = None
            user.save()

            login(request, user)
            request.session.pop("pending_user_id", None)
            request.session.pop("email_sent", None)
            return redirect("student_dashboard")
        else:
            error = "Invalid or expired code. Please try again."

    return render(
        request,
        "accounts/student_verify.html",
        {
            "form": form,
            "error": error,
            "email": getattr(user, "email", ""),
            "email_sent": request.session.get("email_sent", True),
        },
    )


def resend_code(request):
    pending_id = request.session.get("pending_user_id")
    if not pending_id:
        return redirect("student_login")

    user = User.objects.filter(id=pending_id).first()
    if not user:
        return redirect("student_login")

    if not getattr(user, "email", ""):
        return redirect("student_login")

    code = f"{secrets.randbelow(10**6):06d}"
    user.set_verification_code(code, minutes_valid=10)
    user.save()

    sent = safe_send_verification_email(
        user=user,
        code=code,
        subject="Vantage Lingua Hub – Your New Verification Code",
    )
    request.session["email_sent"] = sent

    return redirect("student_verify")


@login_required
def student_dashboard(request):
    # ✅ Must be student
    if not getattr(request.user, "is_student", False):
        return HttpResponseForbidden("Students only.")

    # ✅ Must be authorized
    if not getattr(request.user, "is_authorized", True):
        request.session["pending_user_id"] = request.user.id
        return redirect("student_verify")

    return render(request, "accounts/student_dashboard.html")


def student_logout(request):
    logout(request)
    return redirect("student_login")


def home(request):
    return render(request, "home.html")
