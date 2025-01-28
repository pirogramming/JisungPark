from django.urls import path
from user import views

app_name='user'

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='account_login'),
    path('accounts/signup/', views.CustomSignupView.as_view(), name='account_signup'),
]