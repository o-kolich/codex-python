from django.contrib import admin
from .models import Subject, Course, Module, Text, File, Image, Video, Assignment, Submission, Progress

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'created', 'owner']
    list_filter = ['created', 'subject']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]

admin.site.register(Module)
admin.site.register(Text)
admin.site.register(File)
admin.site.register(Image)
admin.site.register(Video)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Progress)
