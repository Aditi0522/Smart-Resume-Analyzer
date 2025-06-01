from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name= 'main'),
    path('uploaded/', views.upload_success, name='uploaded'),
]
