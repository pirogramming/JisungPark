from django.urls import path
from demos import views
from .views import *

app_name = 'demos'

urlpatterns = [
    path('', views.home, name='home'),  
    path('map/', views.map, name='map'),  
    path('search/', views.search, name='search'),
    path("parking/json/", load_selected_parking_data, name="parking-json"),
    path('service/', views.service, name='service'),
    path('review/', views.review, name='review'),
    path('community/', views.community, name='community'),
    path('work/', views.work, name='work'),
    path('github/', views.github, name='github'),
    path('email/', views.email, name='email'),
    path('insta/', views.insta, name='insta'),
    path('facebook/', views.facebook, name='facebook'),
]
