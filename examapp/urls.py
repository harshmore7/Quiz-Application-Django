from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_student, name='register'),
    path('login/', views.login_student, name='login'),
    path('logout/', views.logout_student, name='logout'),
    path('questions/', views.question_list, name='question_list'),
    path('questions/add/', views.add_question, name='add_question'),
    path('questions/edit/<int:pk>/', views.edit_question, name='edit_question'),
    path('questions/delete/<int:pk>/', views.delete_question, name='delete_question'),
]