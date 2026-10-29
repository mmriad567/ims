from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('teacher/subjects/', views.subject_list, name='subject_list'),
    path('teacher/session/create/<int:subject_id>/', views.session_create, name='session_create'),
    path('teacher/session/<int:session_id>/', views.take_attendance, name='take'),
    path('teacher/attendance/<int:attendance_id>/toggle/', views.toggle_attendance, name='toggle'),
    path('student/attendance/', views.my_attendance, name='my_attendance'),
    path('student/attendance/<int:subject_id>/', views.my_attendance_detail, name='my_attendance_detail'),
]
