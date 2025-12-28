import secrets
import logging

from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .forms import StudentSignUpForm, VerifyCodeForm

User = get_user_model()
logger = logging.getLogger(__name__)


def safe_send_verification_email(user, code, subject):
    message_text = (
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
        if not settings.SENDGRID_API_KEY:
            raise ValueError("SENDGRID_API_KEY not set")
        if not settings.DEFAULT_FROM_EMAIL:
            raise ValueError("DEFAULT_FROM_EMAIL not set")

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        mail = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=user.email,
            subject=subject,
            plain_text_content=message_text,
        )
        sg.send(mail)
        return True

    except Exception as e:
        logger.exception("SendGrid send failed: %s", e)
        print(f"TEMP VERIFY CODE for {user.email} is: {code}")
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
            if user.is_superuser or user.is_staff:
                user.is_authorized = True
                user.save(update_fields=["is_authorized"])
                login(request, user)
                return redirect("/admin/")

            if user.is_student and not user.is_authorized:
                request.session["pending_user_id"] = user.id
                return redirect("student_verify")

            login(request, user)
            return redirect("student_dashboard")

    return render(request, "accounts/student_login.html", {"error": error})


def student_signup(request):
    if request.user.is_authenticated:
        return redirect("student_dashboard")

    form = StudentSignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)

        user.first_name = form.cleaned_data["first_name"].strip()
        user.middle_name = form.cleaned_data.get("middle_name", "").strip()
        user.last_name = form.cleaned_data["last_name"].strip()
        user.email = form.cleaned_data["email"].strip().lower()

        user.is_student = True
        user.is_authorized = False

        user.set_password(form.cleaned_data["password1"])
        user.save()

        code = f"{secrets.randbelow(10**6):06d}"
        print(f"SIGNUP VERIFY CODE for {user.email} is: {code}")

        user.set_verification_code(code, minutes_valid=10)
        user.save()

        sent = safe_send_verification_email(
            user=user,
            code=code,
            subject="Welcome to Vantage Lingua Hub – Verify Your Account",
        )

        request.session["pending_user_id"] = user.id
        request.session["email_sent"] = sent
        return redirect("student_verify")

    return render(request, "accounts/student_signup.html", {"form": form})


def student_verify(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("student_login")

    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("student_login")

    form = VerifyCodeForm(request.POST or None)
    error = None

    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["code"]

        if user.check_verification_code(code):
            user.is_authorized = True
            user.verification_code_hash = ""
            user.verification_code_expires_at = None
            user.save()

            login(request, user)
            request.session.pop("pending_user_id", None)
            request.session.pop("email_sent", None)
            return redirect("student_dashboard")

        error = "Invalid or expired code."

    return render(
        request,
        "accounts/student_verify.html",
        {
            "form": form,
            "error": error,
            "email": user.email,
            "email_sent": request.session.get("email_sent", True),
        },
    )


def resend_code(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("student_login")

    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("student_login")

    code = f"{secrets.randbelow(10**6):06d}"
    print(f"RESEND VERIFY CODE for {user.email} is: {code}")

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
    if not request.user.is_student:
        return HttpResponseForbidden("Students only.")

    if not request.user.is_authorized:
        request.session["pending_user_id"] = request.user.id
        return redirect("student_verify")

    return render(request, "accounts/student_dashboard.html")


def student_logout(request):
    logout(request)
    return redirect("student_login")


def home(request):
    return render(request, "home.html")



@login_required
def student_dashboard(request):
    selected_course = request.GET.get("course", "").strip()

    # Optional: store it so you can use it later (Continue Learning button, etc.)
    if selected_course:
        request.session["selected_course"] = selected_course

    return render(request, "accounts/student_dashboard.html", {
        "selected_course": selected_course or request.session.get("selected_course", ""),
    })