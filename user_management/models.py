from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER = 'USER'
    TEACHER = 'TEACHER'
    ADMIN = 'ADMIN'
    
    ROLE_CHOICES = [
        (USER, 'User'),
        (TEACHER, 'Teacher'),
        (ADMIN, 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    
    def is_user(self):
        return self.role == self.USER
        
    def is_teacher(self):
        return self.role == self.TEACHER
        
    def is_administrator(self):
        return self.role == self.ADMIN
