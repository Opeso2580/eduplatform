from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Course

@login_required
def student_courses(request):
    if not getattr(request.user, "is_student", False):
        return HttpResponseForbidden("Students only.")
    if not getattr(request.user, "is_authorized", True):
        return HttpResponseForbidden("Not authorized.")

    courses = Course.objects.filter(is_published=True).order_by("-created_at")
    return render(request, "courses/student_courses.html", {"courses": courses})

@login_required
def course_detail(request, pk):
    if not getattr(request.user, "is_student", False):
        return HttpResponseForbidden("Students only.")
    if not getattr(request.user, "is_authorized", True):
        return HttpResponseForbidden("Not authorized.")

    course = get_object_or_404(Course, pk=pk, is_published=True)
    return render(request, "courses/course_detail.html", {"course": course})
