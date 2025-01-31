import json 
import os 
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .models import Review, ParkingLot, Post, Comment
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


# Create your views here.
def get_reviews(request):
    user = request.user
    reviews = Review.objects.all().values(
        'user__username', 'rating', 'content'
    )  # 필요한 필드만 가져오기
    reviews_list = list(reviews)
    return JsonResponse({'reviews': reviews_list}, json_dumps_params={'ensure_ascii': False})

@login_required
def get_myreviews(request):
    user = request.user
    reviews = Review.objects.filter(user=user).values(
        'user__username', 'rating', 'content'
    )  # 필요한 필드만 가져오기
    reviews_list = list(reviews)
    return JsonResponse({'reviews': reviews_list}, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def add_review(request):
    if request.method == "POST":
        data = json.loads(request.body)
        rating = data.get('rating')
        content = data.get('content')
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)

        review = Review.objects.create(user=user, rating=rating, content=content)
        return JsonResponse({'message': '리뷰가 추가되었습니다.', 'review': {
            'user': user.username,
            'rating': rating,
            'content': content,
        }})
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

def home(request):
    return render(request, 'home.html')

def load_parking_data(request): # Ajax 요청시 사용
    try:
        parking_data = list(ParkingLot.objects.values())  # QuerySet → 리스트 변환
        return JsonResponse(parking_data, safe=False, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def map(request):   # 페이지 로드시 사용
    parking_data = list(ParkingLot.objects.values())  # QuerySet → 리스트 변환
    return render(request, "map/map.html", {
        "parking_data": json.dumps(parking_data, ensure_ascii=False),  # JSON 변환 추가
        "MAP_KEY": settings.MAP_KEY
    })

def introduce(request):
    return render(request, 'introduce.html')

def review(request):
    return render(request, 'home.html')

def community(request):
    return render(request, 'home.html')

def work(request):
    return render(request, 'home.html')

def github(request):
    return render(request, 'home.html')

def email(request):
    return render(request, 'home.html')

def insta(request):
    return render(request, 'home.html')

def facebook(request):
    return render(request, 'home.html')

def qna(request):
    return render(request, 'qanda.html')

def qanda_list(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)
    qna_list = list(Post.objects.filter(writer=user))
    ctx = {
        'qna_list': qna_list,
    }
    return render(request, 'qanda_list.html', ctx)

