from django.urls import path
from . import views

urlpatterns = [
    path("student/login/", views.student_login, name="student_login"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    path("student/logout/", views.student_logout, name="student_logout"),
]
