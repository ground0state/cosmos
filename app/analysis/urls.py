from django.urls import path
from . import views


app_name = 'analysis'
urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('train/', views.train, name='train'),
    path('predict/', views.predict, name='predict'),
]
