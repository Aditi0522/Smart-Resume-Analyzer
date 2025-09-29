from django.contrib import admin
from .models import Resume, JobDescription, MatchScores

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'docs', 'status', 'date_uploaded']
    list_filter = ['status']

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']

@admin.register(MatchScores)
class MatchScoresAdmin(admin.ModelAdmin):
    list_display = ['resume_id', 'job_id', 'score']
    list_filter = ['job_id']
