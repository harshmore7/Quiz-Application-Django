from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Authentication URLs
    path('register/', views.register_student, name='register'),
    path('login/', views.login_student, name='login'),
    path('logout/', views.logout_student, name='logout'),

    # Question management URLs
    path('questions/', views.question_list, name='question_list'),
    path('questions/add/', views.add_question, name='add_question'),
    path('questions/edit/<int:pk>/', views.edit_question, name='edit_question'),
    path('questions/delete/<int:pk>/', views.delete_question, name='delete_question'),
    path('start-test/', views.start_test, name='start_test'),

    path("start/<int:subject_id>/", views.start_subject_test, name="start_subject_test"),


    path('test/<int:subject_id>/<int:q_index>/', views.test_question, name='test_question'),
    path('end-test/<int:subject_id>/', views.end_test, name='end_test'),
    path('results/', views.result_list, name='result_list'),

    # Student management URLs 
    path('students/', views.student_list, name='student_list'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/delete/<int:pk>/', views.student_delete, name='student_delete'),

    # Profile management URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # Password change URL
    path('profile/password/', views.change_password, name='change_password'),

]