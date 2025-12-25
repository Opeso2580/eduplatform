from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from .forms import StudentLoginForm

def student_login(request):
    if request.user.is_authenticated:
        # if already logged in, go to dashboard
        return redirect("student_dashboard")

    form = StudentLoginForm(request.POST or None)
    error = None

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(request, username=username, password=password)

        if user is None:
            error = "Invalid username or password."
        elif not getattr(user, "is_student", False):
            error = "This login is for students only."
        elif hasattr(user, "is_authorized") and not user.is_authorized:
            error = "Your account is not authorized yet."
        else:
            login(request, user)
            return redirect("student_dashboard")

    return render(request, "accounts/student_login.html", {"form": form, "error": error})

@login_required
def student_dashboard(request):
    if not getattr(request.user, "is_student", False):
        return HttpResponseForbidden("Students only.")
    return render(request, "accounts/student_dashboard.html")

def student_logout(request):
    logout(request)
    return redirect("student_login")
