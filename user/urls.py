from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # ✅ this fixes "/"
    path("student/login/", views.student_login, name="student_login"),
    path("student/signup/", views.student_signup, name="student_signup"),
    path("student/verify/", views.student_verify, name="student_verify"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    path("student/logout/", views.student_logout, name="student_logout"),
    path("student/resend-code/", views.resend_code, name="resend_code"),
]
