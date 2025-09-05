from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Blog
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    
    # Appointments
    path('book/', views.book_appointment, name='book_appointment'),
    path('book/<int:service_id>/', views.book_appointment, name='book_service'),
    path('appointments/', views.my_appointments, name='my_appointments'),
    path('appointment/<int:appointment_id>/confirm/', views.appointment_confirmation, name='appointment_confirmation'),
    path('appointment/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    
    # Reviews
    path('reviews/', views.reviews_list, name='reviews_list'),
    path('services/<int:service_id>/reviews/', views.service_reviews, name='service_reviews'),
    path('appointment/<int:appointment_id>/review/', views.leave_review, name='leave_review'),
    
    # AJAX endpoints
    path('api/available-times/', views.get_available_times_api, name='get_available_times'),
    
    # User management
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('emails/', views.email_history, name='email_history'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]