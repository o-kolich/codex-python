from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.contrib import messages
from django.db.models import Count

from .models import (
    Subject, Course, Module, Text, File, Image, 
    Video, Assignment, Submission, Progress
)
from user_management.models import User

# Custom mixins
class TeacherRequiredMixin(LoginRequiredMixin):
    """Mixin to require teacher or admin role"""
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_teacher() or request.user.is_administrator()):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('user_management:dashboard')
        return super().dispatch(request, *args, **kwargs)

class OwnerRequiredMixin(LoginRequiredMixin):
    """Mixin to require owner of course"""
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user and not request.user.is_administrator():
            messages.error(request, "You don't have permission to modify this content.")
            return redirect('user_management:dashboard')
        return super().dispatch(request, *args, **kwargs)

# Course views
class CourseListView(LoginRequiredMixin, ListView):
    """List all courses based on user role"""
    model = Course
    template_name = 'content_management/course_list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        qs = super().get_queryset()
        # Teachers see their own courses
        if self.request.user.is_teacher():
            return qs.filter(owner=self.request.user)
        # Admins see all courses
        elif self.request.user.is_administrator():
            return qs
        # Students see courses they're enrolled in
        else:
            return qs.filter(students=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subjects'] = Subject.objects.annotate(
            total_courses=Count('courses')
        )
        if self.request.user.is_teacher() or self.request.user.is_administrator():
            context['is_instructor'] = True
        return context

class CourseDetailView(LoginRequiredMixin, DetailView):
    """View course details"""
    model = Course
    template_name = 'content_management/course_detail.html'
    
    def dispatch(self, request, *args, **kwargs):
        course = self.get_object()
        # Check if user has access to this course
        if not (request.user.is_administrator() or 
                request.user == course.owner or 
                course.students.filter(id=request.user.id).exists()):
            messages.error(request, "You don't have access to this course.")
            return redirect('content_management:course_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get user progress for this course if they're a student
        if not (self.request.user.is_teacher() or self.request.user.is_administrator()):
            progress, created = Progress.objects.get_or_create(
                student=self.request.user,
                course=self.object
            )
            context['progress'] = progress
            context['completed_modules'] = progress.completed_modules.all()
        
        # Add owner/instructor context
        if self.request.user == self.object.owner or self.request.user.is_administrator():
            context['is_instructor'] = True
        
        return context

class CourseCreateView(TeacherRequiredMixin, CreateView):
    """Create a new course"""
    model = Course
    fields = ['subject', 'title', 'overview']
    template_name = 'content_management/course_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f"Course '{form.instance.title}' created successfully!")
        return super().form_valid(form)

class CourseUpdateView(OwnerRequiredMixin, UpdateView):
    """Update existing course"""
    model = Course
    fields = ['subject', 'title', 'overview']
    template_name = 'content_management/course_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, f"Course '{form.instance.title}' updated successfully!")
        return super().form_valid(form)

class CourseDeleteView(OwnerRequiredMixin, DeleteView):
    """Delete a course"""
    model = Course
    template_name = 'content_management/course_confirm_delete.html'
    success_url = reverse_lazy('content_management:course_list')
    
    def delete(self, request, *args, **kwargs):
        course = self.get_object()
        messages.success(request, f"Course '{course.title}' deleted successfully!")
        return super().delete(request, *args, **kwargs)

# Module views
class ModuleCreateView(TeacherRequiredMixin, CreateView):
    """Create a new module within a course"""
    model = Module
    fields = ['title', 'description']
    template_name = 'content_management/module_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['course_slug'])
        if self.course.owner != request.user and not request.user.is_administrator():
            messages.error(request, "You don't have permission to add modules to this course.")
            return redirect('content_management:course_detail', slug=self.course.slug)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.course = self.course
        # Set the order to be the next one
        form.instance.order = self.course.modules.count() + 1
        messages.success(self.request, f"Module '{form.instance.title}' added successfully!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        return context
    
    def get_success_url(self):
        return reverse('content_management:course_detail', args=[self.course.slug])

class ModuleDetailView(LoginRequiredMixin, DetailView):
    """View module details"""
    model = Module
    template_name = 'content_management/module_detail.html'
    
    def dispatch(self, request, *args, **kwargs):
        module = self.get_object()
        course = module.course
        # Check if user has access to this module
        if not (request.user.is_administrator() or 
                request.user == course.owner or 
                course.students.filter(id=request.user.id).exists()):
            messages.error(request, "You don't have access to this module.")
            return redirect('content_management:course_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = self.object
        course = module.course
        
        # Check if user is instructor
        if self.request.user == course.owner or self.request.user.is_administrator():
            context['is_instructor'] = True
        
        # For students, check completion status
        if not (self.request.user.is_teacher() or self.request.user.is_administrator()):
            progress = Progress.objects.get(student=self.request.user, course=course)
            context['is_completed'] = module in progress.completed_modules.all()
            context['progress'] = progress
        
        return context

class ModuleUpdateView(OwnerRequiredMixin, UpdateView):
    """Update existing module"""
    model = Module
    fields = ['title', 'description', 'order']
    template_name = 'content_management/module_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context
        
    def dispatch(self, request, *args, **kwargs):
        module = self.get_object()
        if module.course.owner != request.user and not request.user.is_administrator():
            messages.error(request, "You don't have permission to modify this module.")
            return redirect('content_management:course_detail', slug=module.course.slug)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, f"Module '{form.instance.title}' updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('content_management:course_detail', args=[self.object.course.slug])

class ModuleDeleteView(OwnerRequiredMixin, DeleteView):
    """Delete a module"""
    model = Module
    template_name = 'content_management/module_confirm_delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        module = self.get_object()
        if module.course.owner != request.user and not request.user.is_administrator():
            messages.error(request, "You don't have permission to delete this module.")
            return redirect('content_management:course_detail', slug=module.course.slug)
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        course = self.object.course
        messages.success(self.request, f"Module deleted successfully!")
        return reverse('content_management:course_detail', args=[course.slug])

# Content type mapping for polymorphic views
CONTENT_MODELS = {
    'text': Text,
    'file': File,
    'image': Image,
    'video': Video,
    'assignment': Assignment,
}

class ContentCreateView(TeacherRequiredMixin, View):
    """Generic view to create different content types"""
    
    def get(self, request, module_id, content_type):
        module = get_object_or_404(Module, id=module_id)
        
        # Check permissions
        if module.course.owner != request.user and not request.user.is_administrator():
            messages.error(request, "You don't have permission to add content to this module.")
            return redirect('content_management:module_detail', pk=module.id)
        
        # Validate content type
        if content_type not in CONTENT_MODELS:
            messages.error(request, f"Invalid content type: {content_type}")
            return redirect('content_management:module_detail', pk=module.id)
        
        context = {
            'form': None,  # Form would be defined in actual template
            'module': module,
            'content_type': content_type,
        }
        return render(request, f'content_management/content/{content_type}_form.html', context)
    
    def post(self, request, module_id, content_type):
        module = get_object_or_404(Module, id=module_id)
        
        # Check permissions
        if module.course.owner != request.user and not request.user.is_administrator():
            messages.error(request, "You don't have permission to add content to this module.")
            return redirect('content_management:module_detail', pk=module.id)
        
        # Validate content type
        if content_type not in CONTENT_MODELS:
            messages.error(request, f"Invalid content type: {content_type}")
            return redirect('content_management:module_detail', pk=module.id)
        
        # Process the form (form processing would be specific to content type)
        # This is a placeholder - actual implementation would process the form data
        
        messages.success(request, f"{content_type.capitalize()} content added successfully!")
        return redirect('content_management:module_detail', pk=module.id)

class ContentUpdateView(OwnerRequiredMixin, View):
    """Generic view to update different content types"""
    
    def get_object(self):
        content_type = self.kwargs.get('content_type')
        pk = self.kwargs.get('pk')
        
        if content_type not in CONTENT_MODELS:
            raise Http404("Invalid content type")
            
        content_model = CONTENT_MODELS[content_type]
        return get_object_or_404(content_model, id=pk)
    
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        module = self.object.module
        
        if module.course.owner != request.user and not request.user.is_administrator():
            messages.error(request, "You don't have permission to modify this content.")
            return redirect('content_management:module_detail', pk=module.id)
            
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        content_type = kwargs.get('content_type')
        context = {
            'form': None,  # Form would be defined in actual template
            'object': self.object,
            'module': self.object.module,
            'content_type': content_type,
        }
        return render(request, f'content_management/content/{content_type}_form.html', context)
    
    def post(self, request, *args, **kwargs):
        content_type = kwargs.get('content_type')
        module = self.object.module
        
        # Process the form (form processing would be specific to content type)
        # This is a placeholder - actual implementation would process the form data
        
        messages.success(request, f"{content_type.capitalize()} content updated successfully!")
        return redirect('content_management:module_detail', pk=module.id)

class ContentDeleteView(OwnerRequiredMixin, View):
    """Generic view to delete different content types"""
    
    def get_object(self):
        content_type = self.kwargs.get('content_type')
        pk = self.kwargs.get('pk')
        
        if content_type not in CONTENT_MODELS:
            raise Http404("Invalid content type")
            
        content_model = CONTENT_MODELS[content_type]
        return get_object_or_404(content_model, id=pk)
    
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        module = self.object.module
        
        if module.course.owner != request.user and not request.user.is_administrator():
            messages.error(request, "You don't have permission to delete this content.")
            return redirect('content_management:module_detail', pk=module.id)
            
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        content_type = kwargs.get('content_type')
        context = {
            'object': self.object,
            'module': self.object.module,
            'content_type': content_type,
        }
        return render(request, 'content_management/content_confirm_delete.html', context)
    
    def post(self, request, *args, **kwargs):
        content_type = kwargs.get('content_type')
        module = self.object.module
        
        # Delete the object
        self.object.delete()
        
        messages.success(request, f"{content_type.capitalize()} content deleted successfully!")
        return redirect('content_management:module_detail', pk=module.id)

# Enrollment views
class CourseEnrollView(LoginRequiredMixin, View):
    """Enroll a student in a course"""
    
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        
        # Only students can enroll
        if request.user.is_teacher() or request.user.is_administrator():
            messages.error(request, "Only students can enroll in courses.")
            return redirect('content_management:course_detail', slug=slug)
        
        # Check if already enrolled
        if course.students.filter(id=request.user.id).exists():
            messages.info(request, "You are already enrolled in this course.")
        else:
            # Add student to the course
            course.students.add(request.user)
            # Create progress object
            Progress.objects.create(student=request.user, course=course)
            messages.success(request, f"You have successfully enrolled in {course.title}!")
        
        return redirect('content_management:course_detail', slug=slug)

# Progress tracking
class ModuleCompleteView(LoginRequiredMixin, View):
    """Mark a module as completed by a student"""
    
    def post(self, request, pk):
        module = get_object_or_404(Module, id=pk)
        course = module.course
        
        # Only students can mark modules complete
        if request.user.is_teacher() or request.user.is_administrator():
            messages.error(request, "Only students can mark modules as complete.")
            return redirect('content_management:module_detail', pk=pk)
        
        # Check if enrolled in the course
        if not course.students.filter(id=request.user.id).exists():
            messages.error(request, "You must be enrolled in this course.")
            return redirect('content_management:course_list')
        
        # Get or create progress object
        progress, _ = Progress.objects.get_or_create(student=request.user, course=course)
        
        # Toggle completion status
        if module in progress.completed_modules.all():
            progress.completed_modules.remove(module)
            messages.info(request, f"Module '{module.title}' marked as incomplete.")
        else:
            progress.completed_modules.add(module)
            messages.success(request, f"Module '{module.title}' marked as complete!")
        
        return redirect('content_management:module_detail', pk=pk)

# Assignment and submission views
class SubmissionCreateView(LoginRequiredMixin, CreateView):
    """Create a submission for an assignment"""
    model = Submission
    fields = ['file', 'text']
    template_name = 'content_management/submission_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.assignment = get_object_or_404(Assignment, id=kwargs['pk'])
        course = self.assignment.module.course
        
        # Check if user is enrolled in the course
        if not course.students.filter(id=request.user.id).exists():
            messages.error(request, "You must be enrolled in this course to submit assignments.")
            return redirect('content_management:course_list')
            
        # Check if already submitted
        existing = Submission.objects.filter(
            assignment=self.assignment,
            student=request.user
        ).first()
        
        if existing:
            messages.info(request, "You've already submitted this assignment. Editing your submission.")
            return redirect('content_management:submission_update', pk=existing.id)
            
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.assignment = self.assignment
        form.instance.student = self.request.user
        messages.success(self.request, "Assignment submitted successfully!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = self.assignment
        return context
    
    def get_success_url(self):
        return reverse('content_management:module_detail', 
                      args=[self.assignment.module.id])

class SubmissionGradeView(TeacherRequiredMixin, UpdateView):
    """Grade a student submission"""
    model = Submission
    fields = ['grade', 'feedback']
    template_name = 'content_management/submission_grade_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        submission = self.get_object()
        course = submission.assignment.module.course
        
        # Check if user is course owner or admin
        if course.owner != request.user and not request.user.is_administrator():
            messages.error(request, "You don't have permission to grade this submission.")
            return redirect('content_management:course_list')
            
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, "Submission graded successfully!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submission'] = self.object
        context['assignment'] = self.object.assignment
        return context
    
    def get_success_url(self):
        module = self.object.assignment.module
        return reverse('content_management:module_detail', args=[module.id])
