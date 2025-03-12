from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserEditForm, UserPasswordChangeForm
from .models import User

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'user_management/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'user_management/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    user = request.user
    if user.is_administrator():
        return render(request, 'user_management/admin_dashboard.html')
    elif user.is_teacher():
        return render(request, 'user_management/teacher_dashboard.html')
    else:
        return render(request, 'user_management/user_dashboard.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_administrator():
        return redirect('dashboard')
    users = User.objects.all()
    return render(request, 'user_management/admin_dashboard.html', {'users': users})

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher():
        return redirect('dashboard')
    return render(request, 'user_management/teacher_dashboard.html')

@login_required
def user_dashboard(request):
    return render(request, 'user_management/user_dashboard.html')

@login_required
def user_management(request):
    if not request.user.is_administrator():
        return redirect('dashboard')
    
    users = User.objects.all()
    
    if request.method == 'POST' and 'user_id' in request.POST and 'action' in request.POST:
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, id=user_id)
        
        if action == 'delete' and user != request.user:
            user.delete()
            messages.success(request, f"User {user.username} has been deleted.")
            return redirect('user_management')
        
        elif action == 'change_role' and 'new_role' in request.POST:
            new_role = request.POST.get('new_role')
            if new_role in dict(User.ROLE_CHOICES).keys():
                user.role = new_role
                user.save()
                messages.success(request, f"User {user.username}'s role changed to {user.get_role_display()}.")
                return redirect('user_management')
    
    return render(request, 'user_management/user_management.html', {'users': users})

@login_required
def edit_user(request, user_id):
    if not request.user.is_administrator():
        return redirect('dashboard')
        
    user_to_edit = get_object_or_404(User, id=user_id)
    
    # Initialize forms
    user_form = UserEditForm(instance=user_to_edit)
    password_form = UserPasswordChangeForm(user=user_to_edit)
    
    if request.method == 'POST':
        if 'save_details' in request.POST:
            user_form = UserEditForm(request.POST, instance=user_to_edit)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, f"User {user_to_edit.username}'s details updated successfully.")
                return redirect('user_management')
                
        elif 'change_password' in request.POST:
            password_form = UserPasswordChangeForm(user=user_to_edit, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, f"Password for {user_to_edit.username} changed successfully.")
                return redirect('user_management')
    
    context = {
        'user_to_edit': user_to_edit,
        'user_form': user_form,
        'password_form': password_form
    }
    
    return render(request, 'user_management/edit_user.html', context)
