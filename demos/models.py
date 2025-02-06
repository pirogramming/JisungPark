from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class ParkingLot(models.Model):
    name = models.CharField(max_length=255)  # 주차장명
    category = models.CharField(max_length=50, null=True, blank=True)  # 주차장 구분
    type = models.CharField(max_length=50, null=True, blank=True)  # 주차장 유형
    road_address = models.CharField(max_length=255, null=True, blank=True)  # 도로명 주소
    lot_address = models.CharField(max_length=255, null=True, blank=True)  # 지번 주소
    capacity = models.IntegerField(null=True, blank=True)  # 주차구획수
    weekday_start = models.CharField(max_length=10, null=True, blank=True)  # 평일 운영 시작시간
    weekday_end = models.CharField(max_length=10, null=True, blank=True)  # 평일 운영 종료시간
    saturday_start = models.CharField(max_length=10, null=True, blank=True)
    saturday_end = models.CharField(max_length=10, null=True, blank=True)
    holiday_start = models.CharField(max_length=10, null=True, blank=True)
    holiday_end = models.CharField(max_length=10, null=True, blank=True)
    fee_info = models.CharField(max_length=255, null=True, blank=True)  # 요금 정보
    base_time = models.IntegerField(null=True, blank=True)  # 주차 기본 시간
    base_fee = models.IntegerField(null=True, blank=True)  # 주차 기본 요금
    extra_time = models.IntegerField(null=True, blank=True)  # 추가 단위 시간
    extra_fee = models.IntegerField(null=True, blank=True)  # 추가 단위 요금
    payment_method = models.CharField(max_length=50, null=True, blank=True)  # 결제 방법
    phone = models.CharField(max_length=20, null=True, blank=True)  # 전화번호
    latitude = models.FloatField(null=True, blank=True)  # 위도
    longitude = models.FloatField(null=True, blank=True)  # 경도
    disabled_parking = models.BooleanField(default=False)  # 장애인 전용 주차 여부
    average_rating = models.FloatField(null=True, default=None) # 평균 평점


    def __str__(self):
        return f"{self.name} - {self.road_address}"

class LiveInfo(models.Model):
    id = models.AutoField(primary_key=True)
    avail = models.IntegerField(null=False)  # 주차 가능 대수
    update_date = models.DateTimeField(auto_now=True)  # 수정 날짜
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name="live_info")

    def __str__(self):
        return self.parking_lot.name

class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 'auth.User' 대신 settings.AUTH_USER_MODEL 사용
        on_delete=models.CASCADE
    )
    parking_lot = models.ForeignKey(  # 주차장과 연결
        ParkingLot,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,  
        blank=True  #
    )
    rating = models.IntegerField(default=1)  # 평점
    content = models.TextField(blank=True, null=True)  # 리뷰 내용
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    def __str__(self):
        return f"{self.user.username} - {self.rating}"

class Post(models.Model):
    category = models.CharField(max_length=50, null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name='제목')
    content = models.TextField('게시물 내용')
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts', null=True)
    created_date = models.DateTimeField('작성일', auto_now_add=True, null=True, blank=True)
    updated_date = models.DateTimeField('수정일', auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='comments', null=True)
    content = models.TextField('댓글 내용')
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    created_date = models.DateTimeField('작성일', blank=True, auto_created=True, auto_now_add=True)
    updated_date = models.DateTimeField('수정일', blank=True, auto_created=True, auto_now=True)

    def __str__(self):
        return self.content
    
