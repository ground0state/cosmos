from django.urls import path, include
from django.views.generic import RedirectView

from . import views

app_name = 'accounts'
urlpatterns = [
    # path('', RedirectView.as_view(pattern_name='accounts:login', permanent=False)),
    path('signup/', views.SignupView.as_view(), name='signup'),
]
