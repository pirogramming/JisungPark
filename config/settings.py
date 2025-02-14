from pathlib import Path
import environ
import os
import logging
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

env = environ.Env(
    DEBUG=(bool, False)  # DEBUG 값 기본 False 설정
)

# .env 파일이 존재하면 로드
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 환경 변수 적용
DJANGO_KEY = env('DJANGO_KEY')
MAP_KEY = env('MAP_KEY')
SEOUL_KEY = env('SEOUL_KEY')
GYENG_KEY = env('GYENG_KEY')
GOOGLE_ID = env('GOOGLE_ID')
GOOGLE_SECRET = env('GOOGLE_SECRET')
NAVER_ID = env('NAVER_ID')
NAVER_SECRET = env('NAVER_SECRET')
KAKAO_ID = env('KAKAO_ID')
DB_ID = env('DB_USER')
DB_SECRET = env('DB_PASSWORD')
DB_NAME = env('DB_NAME')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = DJANGO_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'demos',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.naver',
    'allauth.socialaccount.providers.google',
    'user',
    'django_celery_beat',
    # allauth - kakao
    'allauth.socialaccount.providers.kakao',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

AUTH_USER_MODEL = 'user.User'  # user는 앱 이름, User는 모델 이름

ACCOUNT_FORMS = {
    'signup': 'user.forms.MyCustomSignupForm',  # 회원가입 폼 커스터마이징
    'login': 'user.forms.MyCustomLoginForm',    # 로그인 폼 커스터마이징
}

SOCIALACCOUNT_LOGIN_ON_GET = True

SITE_ID = 1

LOGIN_REDIRECT_URL = '/'

ACCOUNT_LOGOUT_ON_GET = True

ACCOUNT_CONFIRM_EMAIL_ON_GET = False

ACCOUNT_EMAIL_VERIFICATION = "none"

ACCOUNT_SIGNUP_REDIRECT_URL = '/'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

#✔️‼️📢📢📢📢📢📢호스팅 할 때는 주석 처리하고 올려줘요
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
#‼️✔️✔️✔️📢📢📢📢📢📢호스팅 할 때는 주석 처리 풀어줘요
'''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jisungpark',
        'USER': (f"{DB_ID}"),
        'PASSWORD': (f"{DB_SECRET}"),
        'HOST': (f"{DB_NAME}"),
        'PORT': '3306'
    }
}'''
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
  BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        "APP": {
        "client_id": (f"{GOOGLE_ID}"),
        "secret": (f"{GOOGLE_SECRET}"),
        "key": ""
        },
        "SCOPE": [
            "profile", #구글의 경우 무조건 추가
            "email", # 구글의 경우 무조건 추가
        ],
        "AUTH_PARAMS": {
            "access_type": "online", #추가
            'prompt': 'select_account',#추가 간편로그인을 지원해줌
        }
    },
     "naver": {
        "APP": {
        "client_id": (f"{NAVER_ID}"),
        "secret": (f"{NAVER_SECRET}"),
       "key": ""
        },

        "SCOPE": [

        ],
        #추가
        "AUTH_PARAMS": {
        "access_type": "online",#추가
        'prompt': 'select_account',#추가 간편로그인을 지원해줌
        }},
    "kakao":{
      "APP" : {
        "client_id": (f"{KAKAO_ID}"),
        "secret": "",
        "key": ""
      },
    'AUTH_PARAMS': {'scope': 'profile_nickname, account_email'},
    'METHOD': 'oauth2',
    'VERIFIED_EMAIL': False,
    },
}


# ✅ Redis를 Result Backend로 설정
CELERY_BROKER_URL = 'redis://localhost:6379/0'         # 기존 브로커 설정
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'     # ✅ 결과 백엔드 추가
CELERY_BEAT_SCHEDULE = {
    'fetch-parking-data-every-minute': {
        'task': 'demos.tasks.fetch_parking_data_from_api',
        'schedule': 60.0,  # 1분 간격으로 실행
    },
}
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'
CELERY_ENABLE_UTC = False

#서버 로그 확인
CSRF_TRUSTED_ORIGINS = [
    'https://jisungpark.co.kr/',
    'https://www.jisungpark.co.kr/',
    ]