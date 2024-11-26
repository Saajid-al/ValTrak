from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), #url route from home to views.py
    path('get_user_stats/', views.get_user_stats, name='get_user_stats'),
]
