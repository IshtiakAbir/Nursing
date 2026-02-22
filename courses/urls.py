from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('contact/', views.contact, name='contact'),
    path('branches/', views.branches, name='branches'),
    
    # Authentication
    path('login/', views.student_login, name='login'),
    path('register/', views.student_register, name='register'),
    path('logout/', views.student_logout, name='logout'),

    # Firebase Authentication API
    path('auth/firebase-login/', views.firebase_token_login, name='firebase_login'),
    path('auth/firebase-register/', views.firebase_register_complete, name='firebase_register'),
    
    # Student dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.student_profile, name='my_profile'),
    path('profile/<int:profile_id>/', views.student_profile, name='student_profile'),
    
    # Courses
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    
    # Modules
    path('module/<int:module_id>/', views.module_detail, name='module_detail'),
    
    # Resources
    path('resource/<int:resource_id>/download/', views.download_resource, name='download_resource'),
    

    
    # Certificates
    path('certificate/<int:course_id>/generate/', views.generate_certificate, name='generate_certificate'),
    
    # Announcements
    path('announcements/', views.announcements, name='announcements'),
    path('courses/', views.course_list, name='all_courses'),
]
