from django.urls import path

from . import views

app_name = 'results'

urlpatterns = [
    path('teacher/exams/', views.exam_list, name='exam_list'),
    path(
        'teacher/exams/<int:exam_id>/marks/',
        views.exam_marks_edit,
        name='exam_marks_edit',
    ),
    path('student/result/', views.my_result, name='my_result'),
    path(
        'student/result/<int:subject_id>/',
        views.my_result_detail,
        name='my_result_detail',
    ),
]
