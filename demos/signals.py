import json
import os
import django
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import ParkingLot

def load_parking_data():
    json_file_path = os.path.join(settings.BASE_DIR, "static", "data", "parking_data.json")

    with open(json_file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    parking_records = data.get("records", [])

    # 데이터 저장
    for record in parking_records:
        ParkingLot.objects.get_or_create(
            name=record.get("주차장명", "N/A"),
            road_address=record.get("소재지도로명주소", ""),
            defaults={
                "category": record.get("주차장구분", ""),
                "type": record.get("주차장유형", ""),
                "lot_address": record.get("소재지지번주소", ""),
                "capacity": int(float(record.get("주차구획수", "0") or 0)),
                "weekday_start": record.get("평일운영시작시각", ""),
                "weekday_end": record.get("평일운영종료시각", ""),
                "saturday_start": record.get("토요일운영시작시각", ""),
                "saturday_end": record.get("토요일운영종료시각", ""),
                "holiday_start": record.get("공휴일운영시작시각", ""),
                "holiday_end": record.get("공휴일운영종료시각", ""),
                "fee_info": record.get("요금정보", ""),
                "base_time": int(float(record.get("주차기본시간", "0") or 0)),
                "base_fee": int(float(record.get("주차기본요금", "0") or 0)),
                "extra_time": int(float(record.get("추가단위시간", "0") or 0)),
                "extra_fee": int(float(record.get("추가단위요금", "0") or 0)),
                "payment_method": record.get("결제방법", ""),
                "phone": record.get("전화번호", ""),
                "latitude": float(record.get("위도", "0") or 0),
                "longitude": float(record.get("경도", "0") or 0),
                "disabled_parking": record.get("장애인전용주차구역보유여부", "N") == "Y"
            }
        )

@receiver(post_migrate)
def populate_db(sender, **kwargs):  # migrate하면 자동 저장
    if sender.name == "demos":
        if ParkingLot.objects.exists():  # 데이터 존재시 실행 X
            print("✅ 데이터가 이미 존재합니다. 서버를 실행해주세요!")
            return

        print("🚀 자동으로 주차장 데이터를 DB에 저장하는 중...")
        load_parking_data()
        print("✅ 저장 완료! 서버를 실행해주세요!")
