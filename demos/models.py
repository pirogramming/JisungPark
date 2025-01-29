from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class ParkingLot(models.Model):
    id = models.AutoField(primary_key=True) 
    manage_id = models.CharField(max_length=100, null=False)
    name = models.CharField(max_length=255, null=False)
    parking_type = models.CharField(max_length=50, null=False)  # 추가한 필드_주차장 구분 
    cost_info = models.IntegerField(null=False) #요금 정보보
    basic_time = models.IntegerField(null=False)  # 기본 시간
    basic_cost = models.IntegerField(null=False)  # 기본 요금
    unit_time = models.IntegerField(null=False)  # 추가 단위 시간
    unit_cost = models.IntegerField(null=False)  # 추가 단위 요금
    address = models.CharField(max_length=255, null=False)  # 도로명 주소
    latitude = models.CharField(max_length=50, null=False)  # 위도
    longitude = models.CharField(max_length=50, null=False)  # 경도
    open_day = models.CharField(max_length=50, null=False)  # 운영 요일
    weekday_open = models.CharField(max_length=50, null=False)  # 평일 오픈 시간
    weekday_close = models.CharField(max_length=50, null=False)  # 평일 마감 시간
    saturday_open = models.CharField(max_length=50, null=False)  # 토요일 오픈 시간
    saturday_close = models.CharField(max_length=50, null=False)  # 토요일 마감 시간
    holiday_open = models.CharField(max_length=50, null=False)  # 공휴일 오픈 시간
    holiday_close = models.CharField(max_length=50, null=False)  # 공휴일 마감 시간
    pay_method = models.CharField(max_length=100, null=False)  # 결제 방법
    phone = models.CharField(max_length=50, null=False)  # 전화번호
    disabled_person = models.BooleanField(default=False)  # 장애인 주차구역 보유 여부
    update_date = models.DateTimeField(auto_now=True)  # 수정 날짜

    def __str__(self):
        return f"{self.name} ({self.address})"

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
    rating = models.IntegerField(default=1)  # 평점
    content = models.TextField(blank=True, null=True)  # 리뷰 내용
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    def __str__(self):
        return f"{self.user.username} - {self.rating}"