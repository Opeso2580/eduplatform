from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone

from .models import Course, Enrollment


@login_required
def student_courses(request):
    # ✅ only students
    if not getattr(request.user, "is_student", False):
        return HttpResponseForbidden("Students only.")

    # ✅ must be verified/authorized to use platform
    if not getattr(request.user, "is_authorized", True):
        return HttpResponseForbidden("Not authorized.")

    # ✅ courses this student can actually access (approved by admin)
    approved_enrollments = (
        Enrollment.objects.select_related("course")
        .filter(student=request.user, is_approved=True)
        .order_by("-approved_at", "-requested_at")
    )

    # ✅ show student's approved courses
    approved_courses = [e.course for e in approved_enrollments]

    # ✅ OPTIONAL: show all published courses so student can request access
    published_courses = Course.objects.filter(is_published=True).order_by("-created_at")

    # ✅ which ones student already requested (pending)
    pending_ids = set(
        Enrollment.objects.filter(student=request.user, is_approved=False)
        .values_list("course_id", flat=True)
    )

    return render(
        request,
        "courses/student_courses.html",
        {
            "approved_courses": approved_courses,
            "published_courses": published_courses,
            "pending_ids": pending_ids,
        },
    )


@login_required
def request_course(request, pk):
    # ✅ only students
    if not getattr(request.user, "is_student", False):
        return HttpResponseForbidden("Students only.")

    # ✅ must be verified/authorized to use platform
    if not getattr(request.user, "is_authorized", True):
        return HttpResponseForbidden("Not authorized.")

    course = get_object_or_404(Course, pk=pk, is_published=True)

    # ✅ create enrollment request (pending approval)
    Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={"is_approved": False},
    )

    return redirect("student_courses")


@login_required
def course_detail(request, pk):
    # ✅ only students
    if not getattr(request.user, "is_student", False):
        return HttpResponseForbidden("Students only.")

    # ✅ must be verified/authorized to use platform
    if not getattr(request.user, "is_authorized", True):
        return HttpResponseForbidden("Not authorized.")

    course = get_object_or_404(Course, pk=pk, is_published=True)

    # ✅ student must be approved for this course
    allowed = Enrollment.objects.filter(
        student=request.user,
        course=course,
        is_approved=True
    ).exists()

    if not allowed:
        return HttpResponseForbidden("You are not approved for this course yet.")

    return render(request, "courses/course_detail.html", {"course": course})
