from django.contrib import admin
from django.urls import path


from .views import home, result, index, result1

urlpatterns = [
    path('', home, name='home'),
    path('result', result, name='result'),
    path('result1', result1, name='result1'),
    path('index', index, name='index'),
]