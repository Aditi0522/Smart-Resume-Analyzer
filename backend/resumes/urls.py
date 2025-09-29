from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_resumes, name= 'upload_resumes'),
    path('upload-job/', views.upload_job, name = 'upload_job'),
    path('uploaded/', views.upload_success, name='uploaded'),
    path('matches/', views.matches_view, name='matches'),
]
