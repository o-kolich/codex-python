from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/create/', views.admin_create_user, name='admin_create_user'),
]