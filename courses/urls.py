from django.urls import path
from . import views

urlpatterns = [
    path("student/classes/", views.student_courses, name="student_courses"),
    path("student/classes/<int:pk>/", views.course_detail, name="course_detail"),
]
