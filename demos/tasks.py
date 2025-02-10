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
    pattern1 = r'^(서울특별시|경기도|부산광역시|대구광역시|광주광역시|대전광역시|울산광역시|세종특별자치시|제주특별자치도)\s*'  # 지자체 명으로 시작하는 패턴
    pattern2 = r'-0\b'  # 끝 -0 삭제
    pattern3 = r'\S+\s+\S+\s+\d+(?:-\d*[1-9])?\b'

    address = re.sub(pattern1, '', address)
    address = re.sub(pattern2, '', address)
    if re.fullmatch(pattern3, address):
        #print(address)
        return address
    
    #print('정규화 실패')
    return address
    #정규식 수정 필요
def normalize_phonenumber(number):
    # 지역번호 포함 전화번호 처리
    pattern = r'(\d{2,3})[-)]?(\d{3,4})[-]?(\d{4})' #010 or 02 - 3333 - 3333
    representative_pattern = r'(\d{4})[-]?(\d{4})'  # 1544-5555 같은 패턴

    if re.fullmatch(representative_pattern, number):
        number = re.sub(representative_pattern, r'\1\2', number)
    else:
        number = re.sub(pattern, r'\1\2\3', number)

    return number

'''def response_handle(response):
    if response.status_code == 200:
        data = response.json().get('GetParkingInfo', {}).get('row', [])
        queue = []
        for item in data:
            # 데이터 유효성 검사
            parking_addr = item.get('ADDR', 'unknown').strip().lower()  # 공백 제거 및 소문자 변환
            parking_addr = normalize_address(parking_addr)
            total_capacity = item.get('TPKCT', 0)
            current_vehicles = item.get('NOW_PRK_VHCL_CNT', 0)
            phone_num = item.get('TELNO', '')
            phone_num = normalize_phonenumber(phone_num)
            item_type = item.get("PRK_TYPE_NM", '')
            print(queue)
            # 한 자리씩 여러 개가 존재하는 경우
            if item_type == '노상 주차장':
                if queue and parking_addr not in queue and queue[-1]["saved"]:  # 신규 주차장이며 큐 앞순서 주차장이 저장되어 있는 경우
                    queue.append(
                        {"parking_addr": parking_addr, "total_capacity": total_capacity, "phone_num": phone_num,
                         "saved": False
                            , "current_vehicles": current_vehicles})
                    continue
                elif parking_addr not in queue and len(queue) == 0:  # 신규 주차장이며 큐 맨 앞에 들어오는 경우
                    queue.append(
                        {"parking_addr": parking_addr, "total_capacity": total_capacity, "phone_num": phone_num,
                         "saved": False
                            , "current_vehicles": current_vehicles})
                    continue
                elif parking_addr not in queue and not queue[-1]["saved"]:  # 신규 주차장이며 큐 앞순서 주차장이 redis에 저장이 안된 경우
                    queue[-1]["saved"] = True
                    if not isinstance(queue[-1]["total_capacity"], (int, float)):
                        queue[-1]["total_capacity"] = 0
                    if not isinstance(queue[-1]["current_vehicles"], (int, float)):
                        queue[-1]["current_vehicles"] = 0
                    available_spots = max(0, queue[-1]["total_capacity"] - queue[-1]["current_vehicles"])

                    redis_key_main = f'parking_availability:{queue[-1]["parking_addr"]}'
                    redis_client.setex(redis_key_main, 60, available_spots)  # 1분 TTL 설정

                    # 별칭 Key(phone_num)도 동일한 데이터 가리키도록 설정
                    redis_key_alias = f'parking_info:{queue[-1]["phone_num"]}'
                    redis_client.setex(redis_key_alias, 60, available_spots)  # 1분 TTL 설정

                    logger.info(f'주차장주소 {queue[-1]["parking_addr"]} 데이터 저장 완료 (남은 자리: {available_spots})')
                    queue.append(
                        {"parking_addr": parking_addr, "total_capacity": total_capacity, "phone_num": phone_num,
                         "saved": False
                            , "current_vehicles": current_vehicles})
                    continue
                else:  # 큐에 기존에 존재하는 주차장이며 redis에 저장이 안된 경우
                    queue[-1]["total_capacity"] += total_capacity
                    continue
            elif queue and not queue[-1]["saved"]:  # 노상 주차장이 아니며 큐에 마지막으로 삽입된 것이 redis에 저장이 안된 경우
                queue[-1]["saved"] = True
                if not isinstance(queue[-1]["total_capacity"], (int, float)):
                    queue[-1]["total_capacity"] = 0
                if not isinstance(queue[-1]["current_vehicles"], (int, float)):
                    queue[-1]["current_vehicles"] = 0
                available_spots = max(0, queue[-1]["total_capacity"] - queue[-1]["current_vehicles"])

                redis_key_main = f'parking_availability:{queue[-1]["parking_addr"]}'
                redis_client.setex(redis_key_main, 60, available_spots)  # 1분 TTL 설정

                # 별칭 Key(phone_num)도 동일한 데이터 가리키도록 설정
                redis_key_alias = f'parking_info:{queue[-1]["phone_num"]}'
                redis_client.setex(redis_key_alias, 60, available_spots)  # 1분 TTL 설정

                logger.info(f'주차장주소 {queue[-1]["parking_addr"]} 데이터 저장 완료 (남은 자리: {available_spots})')
            # 노상 주차장이 아니며 큐에 마지막으로 삽입된 것이 redis에 저장된 경우
            # 데이터 타입 검증
            if not isinstance(total_capacity, (int, float)):
                total_capacity = 0
            if not isinstance(current_vehicles, (int, float)):
                current_vehicles = 0

            available_spots = max(0, total_capacity - current_vehicles)  # 음수 방지

            # redis에 저장
            # 기본 Key에 데이터 저장
            redis_key_main = f'parking_availability:{parking_addr}'
            redis_client.setex(redis_key_main, 60, available_spots)  # 1분 TTL 설정

            # 별칭 Key(phone_num)도 동일한 데이터 가리키도록 설정
            redis_key_alias = f'parking_info:{phone_num}'
            redis_client.setex(redis_key_alias, 60, available_spots)  # 1분 TTL 설정

            logger.info(f"주차장주소 '{parking_addr}' 데이터 저장 완료 (남은 자리: {available_spots})")

    else:
        logger.error(f"API 요청 실패: {response.status_code} - {response.text}")
        raise self.retry(exc=Exception(f"API 요청 실패: {response.status_code}"))'''


def response_handle(response):
    if response.status_code == 200:
        data = response.json().get('GetParkingInfo', {}).get('row', [])
        queue = []

        for item in data:
            # 데이터 전처리
            parking_addr = item.get('ADDR', 'unknown').strip().lower()
            parking_addr = normalize_address(parking_addr)
            total_capacity = item.get('TPKCT', 0)
            current_vehicles = item.get('NOW_PRK_VHCL_CNT', 0)
            phone_num = item.get('TELNO', '')
            phone_num = normalize_phonenumber(phone_num)
            item_type = item.get("PRK_TYPE_NM", '')

            # 🚀 [개선] 기존 queue에 동일한 주차장이 있는지 확인
            existing_entry = next((q for q in queue if q["parking_addr"] == parking_addr), None)
            
            if existing_entry:
                # 중복된 주차장일 경우 total_capacity 추가
                existing_entry["total_capacity"] += total_capacity
                existing_entry["current_vehicles"] += current_vehicles
                continue  # 중복된 항목은 새로운 객체를 추가하지 않고 capacity만 업데이트

            # 새로운 주차장 추가
            queue.append({
                "parking_addr": parking_addr,
                "total_capacity": total_capacity,
                "phone_num": phone_num,
                "saved": False,
                "current_vehicles": current_vehicles
            })

        # 🚀 [개선] Redis 저장 로직
        for entry in queue:
            if not entry["saved"]:
                entry["saved"] = True

                # 데이터 타입 검증
                entry["total_capacity"] = entry["total_capacity"] if isinstance(entry["total_capacity"],
                                                                                (int, float)) else 0
                entry["current_vehicles"] = entry["current_vehicles"] if isinstance(entry["current_vehicles"],
                                                                                    (int, float)) else 0
                available_spots = max(0, entry["total_capacity"] - entry["current_vehicles"])

                # Redis 저장
                redis_key_main = f'parking_availability:{entry["parking_addr"]}'
                redis_client.setex(redis_key_main, 60, available_spots)

                redis_key_alias = f'parking_info:{entry["phone_num"]}'
                redis_client.setex(redis_key_alias, 60, available_spots)

                logger.info(f"주차장주소 '{entry['parking_addr']}' 데이터 저장 완료 (남은 자리: {available_spots})")

    else:
        logger.error(f"API 요청 실패: {response.status_code} - {response.text}")
        raise self.retry(exc=Exception(f"API 요청 실패: {response.status_code}"))


@app.task(bind=True, max_retries=3, default_retry_delay=60)  # 자동 재시도 설정
def fetch_parking_data_from_api(self):
    try:
        # 타임아웃 및 예외 처리 추가
        response = requests.get(
            f'http://openapi.seoul.go.kr:8088/{settings.SEOUL_KEY}/json/GetParkingInfo/1/1000',
            timeout=10  # 10초 타임아웃 설정
        )
        response2 = requests.get(
            f'http://openapi.seoul.go.kr:8088/{settings.SEOUL_KEY}/json/GetParkingInfo/1001/1875',
            timeout=10  # 10초 타임아웃 설정
        )

        response_handle(response)
        response_handle(response2)


    except requests.exceptions.RequestException as e:
        logger.error(f"네트워크 오류 발생: {e}")
        raise self.retry(exc=e)  # 네트워크 오류 시 재시도

    except Exception as e:
        logger.error(f"API 호출 오류: {e}")
        raise self.retry(exc=e)  # 기타 오류 시 재시도