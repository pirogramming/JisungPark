import json
import redis
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.conf import settings

from user.models import User
from .models import UserFavoriteParking, Review, ParkingLot, Post, Comment
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import CommentForm, MyInfoForm
from .tasks import normalize_phonenumber
import logging
from django.contrib.auth import logout

logger = logging.getLogger(__name__)
# 주소 비교
def normalize_address(address):
    pattern1 = r'^(서울특별시|경기도|부산광역시|대구광역시|광주광역시|대전광역시|울산광역시|세종특별자치시|제주특별자치도)\s*'  # 지자체 명으로 시작하는 패턴
    pattern2 = r'-0\b'  # 끝 -0 삭제
    pattern3 = r'\S+\s+\S+\s+\d+(?:-\d*[1-9])?\b'
    pattern4 = r'\s\(.*?\)'

    address = re.sub(pattern1, '', address)
    address = re.sub(pattern2, '', address)
    address = re.sub(pattern4, '', address)
    if re.fullmatch(pattern3, address):
        # print(address)
        return address

    # print('정규화 실패')
    return address

# Create your views here.
def get_reviews(request, parking_lot_id):
    reviews = Review.objects.filter(parking_lot_id=parking_lot_id).values(
        'user__username', 'rating', 'content', 'id'
    )  # 필요한 필드만 가져오기
    reviews_list = list(reviews)
    return JsonResponse({'reviews': reviews_list}, json_dumps_params={'ensure_ascii': False})

@login_required
def get_myreviews(request):
    user = request.user
    myreviews = Review.objects.filter(user=user).values(
        'user__username', 'rating', 'content', 'id','parking_lot__id' 
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

        if Review.objects.filter(user=user, parking_lot=ParkingLot.objects.get(id=parking_lot_id)).exists():
            return JsonResponse({'error': '유저는 한 주차장 당 한 개의 리뷰만 작성 가능합니다.'}, status=400)

        if not user.is_authenticated:
            return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)
        try:
                parking_lot = ParkingLot.objects.get(id=parking_lot_id)
        except ParkingLot.DoesNotExist:
            return JsonResponse({'error': '해당 주차장이 존재하지 않습니다.'}, status=400)

        review = Review.objects.create(user=user, rating=rating, content=content,parking_lot=parking_lot,)
        review_list = Review.objects.filter(parking_lot=parking_lot)
        parking_lot.average_rating = (parking_lot.average_rating * (len(review_list)-1) + review.rating) / len(review_list)
        
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
            "id", "name", "lot_address", "capacity", "latitude", "longitude",
            "base_time", "base_fee", "extra_time", "extra_fee",
            "fee_info", "type", "disabled_parking", "average_rating",
            "phone", "capacity", "weekday_start", "weekday_end", "saturday_start",
            "saturday_end", "holiday_start", "holiday_end"
        ))

        def convert_to_int(value):
            """ Redis 데이터를 정수로 변환하는 함수 """
            if value is None:
                return value
            try:
                return int(float(value.decode())) if isinstance(value, bytes) else int(float(value))
            except ValueError:
                return None

        for lot in parking_data:
            parking_addr = lot['lot_address']
            phone_num = lot['phone']
            second_available_spots = None

            parking_addr = normalize_address(parking_addr)  # 주소 정규화
            redis_key = f'parking_availability:{parking_addr}'
            available_spots = convert_to_int(redis_client.get(redis_key))

            if phone_num and phone_num.strip() != '':  # 전화번호가 공백이 아닐 때만
                phone_num = normalize_phonenumber(phone_num)
                redis_subkey = f'parking_info:{phone_num}'
                second_available_spots = convert_to_int(redis_client.get(redis_subkey))

            # 🚀 올바른 방식으로 남은 자리 설정
            if available_spots and available_spots >= 0:
                lot['available_spots'] = available_spots
            elif second_available_spots and second_available_spots >= 0:
                lot['available_spots'] = second_available_spots
            else:
                lot['available_spots'] = None
            #print(f"📌 주소: {parking_addr}, Redis 주차 가능 자리: {available_spots}, 전화번호 기반 자리: {second_available_spots}")

        # 🚀 JSON 배열([])로 반환
        return JsonResponse(parking_data, safe=False, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



def map(request):   # 페이지 로드시 사용
    parking_id = request.GET.get('parking_id')  # URL에서 parking_id 가져오기
    parking_data = ParkingLot.objects.values("id", "name", "lot_address", "latitude", "longitude", "base_time", "base_fee", "extra_time", "extra_fee", "fee_info", "type", "disabled_parking", "average_rating", "phone", "capacity", "weekday_start", "weekday_end", "saturday_start", "saturday_end", "holiday_start", "holiday_end")
    enriched_data = []

    def convert_to_int(value):
        """ Redis 데이터를 정수로 변환하는 함수 """
        if value is None:
            return value
        try:
            return int(float(value.decode())) if isinstance(value, bytes) else int(float(value))
        except ValueError:
            return None

    selected_parking = None  # 특정 주차장 정보 저장할 변수

    for lot in parking_data:
        parking_addr = lot['lot_address']
        phone_num = lot['phone']
        second_available_spots = None

        parking_addr = normalize_address(parking_addr)  # 주소 정규화
        redis_key = f'parking_availability:{parking_addr}'
        available_spots = convert_to_int(redis_client.get(redis_key))

        if phone_num and phone_num.strip() != '':  # 전화번호가 공백이 아닐 때만
            phone_num = normalize_phonenumber(phone_num)
            redis_subkey = f'parking_info:{phone_num}'
            second_available_spots = convert_to_int(redis_client.get(redis_subkey))

        # 🚀 올바른 방식으로 남은 자리 설정
        if available_spots and available_spots >= 0:
            lot['available_spots'] = available_spots
        elif second_available_spots and second_available_spots >= 0:
            lot['available_spots'] = second_available_spots
        else:
            lot['available_spots'] = None

        enriched_data.append(lot)

        # 🚀 특정 `parking_id`가 있으면 해당 주차장 데이터 저장
        if parking_id and str(lot["id"]) == parking_id:
            selected_parking = lot

    context = {
        "parking_data": json.dumps(enriched_data, ensure_ascii=False),
        "MAP_KEY": settings.MAP_KEY,
        "selected_parking": json.dumps(selected_parking, ensure_ascii=False) if selected_parking else None,  # 특정 주차장 정보 전달
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
            if (review.user != request.user) and not (request.user.is_superuser):
                return JsonResponse({"message": "리뷰는 본인만 삭제 가능합니다."}, status=200)
            parking_lot = review.parking_lot
            review_list = Review.objects.filter(id=review_id)
            parking_lot.average_rating = (parking_lot.average_rating * (len(review_list) - 1) - review.rating) / (len(review_list)-2)
            parking_lot.save()
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

@csrf_exempt
def toggle_favorite(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "로그인이 필요합니다."}) 

    if request.method == "POST":
        data = json.loads(request.body)
        parking_id = data.get("parking_id")
        user = request.user

        try:
            parking_lot = get_object_or_404(ParkingLot, id=parking_id)
        except ParkingLot.DoesNotExist:
            return JsonResponse({"error": "주차장을 찾을 수 없습니다."}, status=404)

        favorite, created = UserFavoriteParking.objects.get_or_create(user=user, parking_lot=parking_lot)

        if not created:
            favorite.delete()
            return JsonResponse({"message": "찜이 해제되었습니다.", "favorited": False})

        return JsonResponse({"message": "주차장이 찜되었습니다.", "favorited": True})

    return JsonResponse({"error": "잘못된 요청 방식입니다."}, status=400)

@login_required
def get_favorites(request):
    favorites = UserFavoriteParking.objects.filter(user=request.user).select_related("parking_lot")
    favorite_list = [
        {"id": fav.parking_lot.id, "name": fav.parking_lot.name, "address": fav.parking_lot.lot_address}
        for fav in favorites
    ]
    return JsonResponse({"liked_parking_lots": favorite_list}, safe=False)

def get_parking(request, parking_lot_id):
    """
    특정 주차장 상세 정보를 반환하는 API
    """
    try:
        parking = ParkingLot.objects.get(id=parking_lot_id)
        parking_data = {
            "id": parking.id,
            "주차장명": parking.name,
            "요금정보": parking.fee_info,
            "주차장유형": parking.type,
            "장애인전용주차구역보유여부": parking.disabled_parking, 
            "남은자리": parking.available_spots if parking.available_spots is not None else "정보 없음"

        }
        return JsonResponse(parking_data)
    except ParkingLot.DoesNotExist:
        return JsonResponse({"error": "해당 주차장이 존재하지 않습니다."}, status=404)

def mypage_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)  # 사용자 객체 가져오기
    form = MyInfoForm(instance=user)  # 기존 사용자 정보로 폼 초기화

    if request.method == "POST":
        form = MyInfoForm(request.POST, instance=user)  # 기존 유저 정보 갱신
        if form.is_valid():
            form.save()  # 사용자 정보 저장
            return render(request, "mypage.html", {"user_id": user_id, "form": form, "message": "정보가 수정되었습니다!"})

    ctx = {
        "user_id": user_id,
        "form": form,
    }
    return render(request, "mysetting.html", ctx)

def withdraw_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)  # 유저 조회
        logout(request)  # 로그아웃
        user.delete()  # 사용자 삭제

        return JsonResponse({"message": "회원 탈퇴가 완료되었습니다."}, status=200)

    return JsonResponse({"error": "잘못된 요청입니다."}, status=400)
