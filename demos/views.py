import json 
import os 
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings

# Create your views here.
def home(request):
    return render(request, 'home.html')

def map(request):
    return render(request, 'map.html')

def search(request):
    return render(request, 'map.html')

# def load_selected_parking_data(request=None):  # request 기본값을 None으로 설정
#     try:
#         json_file_path = os.path.join(settings.BASE_DIR, "parking_data.json")

#         with open(json_file_path, "r", encoding="utf-8") as json_file:
#             data = json.load(json_file)

#         parking_records = data.get("records", [])

#         required_fields = ["주차장명", "소재지도로명주소", "주차구획수", "위도", "경도"]

#         filtered_parking_data = [
#             {field: record.get(field, "N/A") for field in required_fields}
#             for record in parking_records
#         ]

#         #  `request`가 제공되었으면 JSON 응답 반환 (뷰에서 호출할 때)
#         if request is not None:
#             return JsonResponse(filtered_parking_data, safe=False, json_dumps_params={'ensure_ascii': False})

#         # `request`가 없으면 리스트 반환 (map 뷰에서 내부적으로 호출할 때)
#         return filtered_parking_data

#     except Exception as e:
#         error_response = {"error": str(e)}
#         return JsonResponse(error_response, status=500) if request is not None else []

def load_selected_parking_data(request):
    try:
        json_file_path = os.path.join(settings.BASE_DIR, "parking_data.json")
        # JSON 파일 열기
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        # JSON 데이터에서 "records" 키 가져오기
        parking_records = data.get("records", [])
        # 선택할 필드 
        required_fields = [
            "주차장명", "주차장구분", "주차장유형", "소재지도로명주소", "소재지지번주소",
            "주차구획수", "운영요일", "평일운영시작시각", "평일운영종료시각",
            "토요일운영시작시각", "토요일운영종료시각", "공휴일운영시작시각", "공휴일운영종료시각",
            "요금정보", "주차기본시간", "주차기본요금", "추가단위시간", "추가단위요금",
            "결제방법", "전화번호", "위도", "경도", "장애인전용주차구역보유여부"
        ]
        # 필요한 필드만 선택해 새로운 리스트 생성
        filtered_parking_data = [
            {field: record.get(field, "N/A") for field in required_fields}  # 없는 값은 N/A
            for record in parking_records
        ]
        return JsonResponse(filtered_parking_data, safe=False, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def map(request):
    response = load_selected_parking_data(request)  # request 전달 
    parking_data = json.loads(response.content)  # Jsonresponse엔서 json 데이터 가져옴옴
    return render(request, "map.html", {"parking_data": parking_data})

def service(request):
    return render(request, 'home.html')

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