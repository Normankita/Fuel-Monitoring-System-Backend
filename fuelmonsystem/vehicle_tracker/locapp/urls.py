# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.data_list, name='data_list'),
    path('dlte/', views.data_delete, name='data_list')
]
