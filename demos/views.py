import json
import redis
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.conf import settings
from .models import Review, ParkingLot, Post, Comment
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import CommentForm

# 주소 비교
def normalize_address(address):
    # "서울특별시" 제거
    address = re.sub(r'^서울특별시\s*', '', address)

    # 숫자 뒤에 "-"가 오고 또 숫자가 올 경우, 첫 번째 숫자만 남김
    address = re.sub(r'(\d+)-\d+', r'\1', address)

    # 모든 숫자를 정수 형태로 변환 (앞에 0이 있는 경우 제거)
    address = re.sub(r'\b\d+\b', lambda x: str(int(x.group())), address)

    return address

# Create your views here.
def get_reviews(request, parking_lot_id):
    reviews = Review.objects.filter(parking_lot_id=parking_lot_id).values(
        'user__username', 'rating', 'content'
    )  # 필요한 필드만 가져오기
    reviews_list = list(reviews)
    return JsonResponse({'reviews': reviews_list}, json_dumps_params={'ensure_ascii': False})

@login_required
def get_myreviews(request):
    user = request.user
    myreviews = Review.objects.filter(user=user).values(
        'user__username', 'rating', 'content'
    )  # 필요한 필드만 가져오기
    reviews_list = list(myreviews)
    return JsonResponse({'reviews': reviews_list}, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def add_review(request):
    if request.method == "POST":
        data = json.loads(request.body)
        rating = data.get('rating')
        content = data.get('content')
        parking_lot_id = data.get('parking_lot_id')  # 주차장 ID 받기
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)
        try:
                parking_lot = ParkingLot.objects.get(id=parking_lot_id)
        except ParkingLot.DoesNotExist:
            return JsonResponse({'error': '해당 주차장이 존재하지 않습니다.'}, status=400)

        review = Review.objects.create(user=user, rating=rating, content=content,parking_lot=parking_lot,)
        review_list = Review.objects.filter(parking_lot=parking_lot)
        parking_lot.average_rating = (parking_lot.average_rating * (len(review_list)-1) + review.rating) / len(review_list)
        #print(parking_lot.average_rating)
        parking_lot.save()
        return JsonResponse({'message': '리뷰가 추가되었습니다.', 'review': {
            'user': user.username,
            'parking_lot': parking_lot.name,
            'rating': rating,
            'content': content,
        }})
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

def home(request):
    return render(request, 'home.html')

# Redis 설정
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# 수정된 코드 (views.py)
def load_parking_data(request):
    try:
        parking_data = list(ParkingLot.objects.values(
            "id", "name", "lot_address", "latitude", "longitude",
            "base_time", "base_fee", "extra_time", "extra_fee",
            "fee_info", "type", "disabled_parking", "average_rating"
        ))
        for lot in parking_data:
            parking_addr = lot['lot_address']
            parking_addr = normalize_address(parking_addr)  # 주소 정규화
            redis_key = f'parking_availability:{parking_addr}'  # 일관된 키 사용
            available_spots = redis_client.get(redis_key)
            
            ### if available_spots!=None:
                ### print(available_spots)

            lot['available_spots'] = (available_spots) if available_spots else 0
            
            ### if lot['available_spots'] != None and lot['available_spots']!=0 and lot['available_spots']!='0':
                ### print(lot['available_spots'])


        return JsonResponse(parking_data, safe=False, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



def map(request):   # 페이지 로드시 사용
    parking_data = ParkingLot.objects.values("id", "name", "lot_address", "latitude", "longitude", "base_time", "base_fee", "extra_time", "extra_fee", "fee_info", "type", "disabled_parking")

    enriched_data = []
    for lot in parking_data:
        parking_addr = lot['lot_address']
        redis_key = f'parking_availability:{parking_addr}'
        available_spots = redis_client.get(redis_key)

        # 실시간 데이터 추가
        lot['available_spots'] = available_spots if available_spots else 0
        enriched_data.append(lot)

    context = {
        "parking_data": json.dumps(enriched_data, ensure_ascii=False),
        "MAP_KEY": settings.MAP_KEY
    }
    return render(request, "map/map.html", context)

def introduce(request):
    return render(request, 'introduce.html')

def aboutus(request):
    return render(request, 'aboutus.html')

def guidemap(request):
    return render(request, 'guidemap.html')

def qna(request):
    return render(request, 'qanda.html')

def mypage(request):
    return render(request, 'mypage.html')

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

@login_required
def qanda_list(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)
    if user.is_superuser:
        qna_list = list(Post.objects.all().values())
        ctx = {'qna_list': qna_list}
        return render(request, 'qanda_list.html', ctx)
    qna_list = list(Post.objects.filter(writer=user))
    ctx = {
        'qna_list': qna_list,
    }
    return render(request, 'qanda_list.html', ctx)

@login_required
def qna_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    comments = Comment.objects.filter(post=post, parent_comment__isnull=True)  # 부모 댓글만 가져오기
    form = CommentForm()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.writer = request.user  # 현재 로그인한 사용자

            parent_id = request.POST.get('parent_comment_id')
            if parent_id:  # 대댓글이면
                comment.parent_comment = Comment.objects.get(id=parent_id)

            comment.save()
            return redirect("demos:qna_detail", pk=post.id)  # 저장 후 리디렉션

    return render(request, 'qanda_room.html', {'post': post, 'comments': comments, 'form': form})

@login_required
def qanda_create(request):
    if request.method == 'POST':
        post = Post.objects.create(
            category = 'qna',
            title=request.POST['title'],
            content=request.POST['content'],
            writer=request.user,
        )
        return redirect("demos:qna_detail", pk=post.pk)
    return render(request, 'qanda_create.html')
@login_required
def qanda_update(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']

        post.title = title
        post.content = content
        post.save()
        return redirect("demos:qna_detail", pk=post.pk)

    ctx = {'post':post}
    return render(request, 'qanda_update.html', ctx)

@login_required
def qanda_delete(request, pk):
    post = get_object_or_404(Post, id=pk)
    post.delete()
    return redirect("demos:qanda_list")


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # 댓글 작성자만 삭제 가능하도록 제한
    if comment.writer != request.user:
        return HttpResponseForbidden("삭제할 권한이 없습니다.")

    comment.delete()
    return redirect('demos:qna_detail', comment.post.id)  # 댓글이 달린 게시글 상세 페이지로 이동

@csrf_exempt
def delete_review(request, review_id):
    if request.method == "DELETE":
        try:
            review = Review.objects.get(id=review_id)
            review.delete()
            return JsonResponse({"message": "리뷰가 삭제되었습니다."}, status=200)
        except Review.DoesNotExist:
            return JsonResponse({"error": "리뷰를 찾을 수 없습니다."}, status=404)
    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=400)

@csrf_exempt
def update_review(request, review_id):
    if request.method == "PATCH":
        try:
            review = Review.objects.get(id=review_id)
            data = json.loads(request.body)
            review.content = data.get("content", review.content)  # 기존 값 유지
            review.rating = data.get("rating", review.rating)
            review.save()
            return JsonResponse({"message": "리뷰가 수정되었습니다."}, status=200)
        except Review.DoesNotExist:
            return JsonResponse({"error": "리뷰를 찾을 수 없습니다."}, status=404)
    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=400)