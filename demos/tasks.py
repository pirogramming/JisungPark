from celery import shared_task
import requests
import redis
import json

# Redis 클라이언트
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

@shared_task
def fetch_parking_data_from_api():
    try:
        response = requests.get('https://api.example.com/parking')
        if response.status_code == 200:
            data = response.json()
            for item in data:
                parking_address = item.get('address')
                available_spots = item.get('available_spots', 0)

                # Redis에 저장 (Key: 주차장 주소 기반)
                redis_client.set(f'parking_availability:{parking_address}', available_spots)
        else:
            print(f"API 요청 실패: {response.status_code}")
    except Exception as e:
        print(f"API 호출 오류: {e}")
