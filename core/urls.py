from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.dashboard, name='dashboard'),
    path('classrooms/join/', views.join_classroom, name='join_classroom'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:pk>/submit/', views.submit_responses, name='submit_responses'),
    # Teacher views
    path('t/classrooms/', views.my_classrooms, name='my_classrooms'),
    path('t/classrooms/new/', views.create_classroom, name='create_classroom'),
    path('t/classrooms/<int:class_id>/', views.teacher_classroom, name='teacher_classroom'),
    path('t/assignments/<int:pk>/', views.teacher_assignment_detail, name='teacher_assignment_detail'),
    path('t/responses/<int:resp_id>/', views.review_response, name='review_response'),
    path('t/classrooms/<int:class_id>/assignments/new/', views.create_assignment, name='create_assignment'),
    ]