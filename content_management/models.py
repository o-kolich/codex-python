from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse

class Subject(models.Model):
    """Subject categories for courses"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Course(models.Model):
    """Main course container"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    subject = models.ForeignKey(Subject, related_name='courses', on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, 
                             related_name='courses_created',
                             on_delete=models.CASCADE)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     related_name='courses_enrolled',
                                     blank=True)
    
    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('content_management:course_detail', args=[self.slug])

class Module(models.Model):
    """Course modules/sections"""
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f'{self.order}. {self.title}'

class Content(models.Model):
    """Abstract base model for content types"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        abstract = True
        ordering = ['order']
    
    def __str__(self):
        return self.title

class Text(Content):
    """Text content type"""
    content = models.TextField()

class File(Content):
    """File upload content type"""
    file = models.FileField(upload_to='files')

class Image(Content):
    """Image content type"""
    image = models.ImageField(upload_to='images')

class Video(Content):
    """Video content type (embed URL)"""
    url = models.URLField()

class Assignment(Content):
    """Assignment content type"""
    description = models.TextField()
    due_date = models.DateTimeField()
    points = models.PositiveIntegerField(default=100)
    
class Submission(models.Model):
    """Student assignment submissions"""
    assignment = models.ForeignKey(Assignment, related_name='submissions', on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submissions', on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions', blank=True, null=True)
    text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f'{self.student.username} - {self.assignment.title}'

class Progress(models.Model):
    """Track student progress through course content"""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='progress', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='progress', on_delete=models.CASCADE)
    completed_modules = models.ManyToManyField(Module, related_name='completed_by', blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f'{self.student.username} - {self.course.title}'
