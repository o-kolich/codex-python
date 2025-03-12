from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
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
