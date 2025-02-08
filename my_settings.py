DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # mysqlclient library 설치
        'NAME': 'jisungpark',
        'USER': 'root',
        'PASSWORD': 'toor', # mariaDB 설치 시 입력한 root 비밀번호 입력
        'HOST': 'localhost',
        'PORT': '3400'
    }
}