from django.urls import path
from .views import *

app_name = 'demos'

urlpatterns = [
    path('', views.home, name='home'),  
    path('login/',views.login, name='login'),
    path('signin/', views.signin, name='signin'),  
    path('signup/', views.signup, name='signup'),  
    path('map/', views.map, name='map'),  
]
