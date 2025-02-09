from config.celery_app import app
from django.conf import settings
import requests
import redis
import logging
import re

# 로깅 설정
logger = logging.getLogger(__name__)

# Redis 클라이언트 설정 (한 번만 설정하고 재사용)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def normalize_address(address):
    # "서울특별시" 제거
    address = re.sub(r'^서울특별시\s*', '', address)

    # 숫자 뒤에 "-"가 오고 또 숫자가 올 경우, 첫 번째 숫자만 남김
    address = re.sub(r'(\d+)-\d+', r'\1', address)

    # 모든 숫자를 정수 형태로 변환 (앞에 0이 있는 경우 제거)
    address = re.sub(r'\b\d+\b', lambda x: str(int(x.group())), address)

    return address

@app.task(bind=True, max_retries=3, default_retry_delay=60)  # 자동 재시도 설정
def fetch_parking_data_from_api(self):
    try:
        # 타임아웃 및 예외 처리 추가
        response = requests.get(
            f'http://openapi.seoul.go.kr:8088/{settings.SEOUL_KEY}/json/GetParkingInfo/1/1000',
            timeout=10  # 10초 타임아웃 설정
        )

        if response.status_code == 200:
            data = response.json().get('GetParkingInfo', {}).get('row', [])
            for item in data:
                # 데이터 유효성 검사
                parking_addr = item.get('ADDR', 'unknown').strip().lower()  # 공백 제거 및 소문자 변환
                parking_addr = normalize_address(parking_addr)
                total_capacity = item.get('TPKCT', 0)
                current_vehicles = item.get('NOW_PRK_VHCL_CNT', 0)
                phone_num = item.get('TELNO', '')

                # 데이터 타입 검증
                if not isinstance(total_capacity, (int, float)):
                    total_capacity = 0
                if not isinstance(current_vehicles, (int, float)):
                    current_vehicles = 0

                available_spots = max(0, total_capacity - current_vehicles)  # 음수 방지

                # redis에 저장
                # 기본 Key에 데이터 저장
                redis_key_main = f'parking_info:{parking_addr}'
                redis_client.setex(redis_key_main, 60, available_spots)  # 1분 TTL 설정

                # 별칭 Key(phone_num)도 동일한 데이터 가리키도록 설정
                redis_key_alias = f'parking_info:{phone_num}'
                redis_client.setex(redis_key_alias, 60, available_spots)  # 1분 TTL 설정

                logger.info(f"주차장주소 '{parking_addr}' 데이터 저장 완료 (남은 자리: {available_spots})")

        else:
            logger.error(f"API 요청 실패: {response.status_code} - {response.text}")
            raise self.retry(exc=Exception(f"API 요청 실패: {response.status_code}"))

    except requests.exceptions.RequestException as e:
        logger.error(f"네트워크 오류 발생: {e}")
        raise self.retry(exc=e)  # 네트워크 오류 시 재시도

    except Exception as e:
        logger.error(f"API 호출 오류: {e}")
        raise self.retry(exc=e)  # 기타 오류 시 재시도