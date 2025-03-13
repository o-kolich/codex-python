from django.urls import path
from . import views

app_name = 'content_management'

urlpatterns = [
    # Course patterns
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('course/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('course/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('course/<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    path('course/<slug:slug>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    
    # Module patterns
    path('course/<slug:course_slug>/module/create/', views.ModuleCreateView.as_view(), name='module_create'),
    path('module/<int:pk>/', views.ModuleDetailView.as_view(), name='module_detail'),
    path('module/<int:pk>/edit/', views.ModuleUpdateView.as_view(), name='module_update'),
    path('module/<int:pk>/delete/', views.ModuleDeleteView.as_view(), name='module_delete'),
    
    # Content patterns (using content type polymorphism)
    path('module/<int:module_id>/content/<str:content_type>/create/', 
         views.ContentCreateView.as_view(), name='content_create'),
    path('content/<str:content_type>/<int:pk>/edit/', 
         views.ContentUpdateView.as_view(), name='content_update'),
    path('content/<str:content_type>/<int:pk>/delete/', 
         views.ContentDeleteView.as_view(), name='content_delete'),
    
    # Student enrollment
    path('course/<slug:slug>/enroll/', views.CourseEnrollView.as_view(), name='course_enroll'),
    
    # Student progress
    path('module/<int:pk>/complete/', views.ModuleCompleteView.as_view(), name='module_complete'),
    
    # Assignment and submission
    path('assignment/<int:pk>/submit/', views.SubmissionCreateView.as_view(), name='submission_create'),
    path('submission/<int:pk>/grade/', views.SubmissionGradeView.as_view(), name='submission_grade'),
]