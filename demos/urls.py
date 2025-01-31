from django.urls import path
from demos import views
from .views import *

app_name = 'demos'

urlpatterns = [
    path('', views.home, name='home'),  
    path('map/', views.map, name='map'),  
    path('introduce/', views.introduce, name='introduce'),
    path('review/', views.review, name='review'),
    path('community/', views.community, name='community'),
    path('work/', views.work, name='work'),
    path('github/', views.github, name='github'),
    path('email/', views.email, name='email'),
    path('insta/', views.insta, name='insta'),
    path('facebook/', views.facebook, name='facebook'),
    path('api/reviews/', views.get_reviews, name='get_reviews'),
    path('api/add_review/', views.add_review, name='add_review'),
    path('qna/', views.qna, name='qna'),
    path('qna/list/', views.qanda_list, name='qanda_list'),
]