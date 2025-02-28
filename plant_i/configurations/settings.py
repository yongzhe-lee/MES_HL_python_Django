"""
Django settings for qm_lims project.

Based on 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import posixpath
from pathlib import Path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '57882419-5a5a-47ee-93b9-7f822cc69dd5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application references
# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-INSTALLED_APPS
INSTALLED_APPS = [
    'app',                                      # 사용자가 만든 앱 이름
    # Add your apps here to enable them         
    'django.contrib.admin',                     # Django 관리(admin) 사이트
    'django.contrib.auth',                      # 인증(authentication) 시스템 (사용자, 권한 관리)
    'django.contrib.contenttypes',              # 콘텐츠 타입 시스템 (데이터베이스 모델을 처리)
    'django.contrib.sessions',                  # 세션 관리
    'django.contrib.messages',                  # 메시징 프레임워크 (알림 등)
    'django.contrib.staticfiles',               # 정적 파일 관리 (CSS, JS 등)
    'domain',                                   # 사용자가 만든 domain 앱
]

# Middleware framework
# https://docs.djangoproject.com/en/2.1/topics/http/middleware/
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'configurations.urls'

# Template configuration
# https://docs.djangoproject.com/en/2.1/topics/templates/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
if DEBUG:
    default_loaders = [
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    ]

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
            #'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
                "loaders": default_loaders,
            },
        },
    ]

WSGI_APPLICATION = 'configurations.wsgi.application'
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DBMS_HOST = '10.10.10.231'      # 개발
# DBMS_HOST = '10.226.236.34'   # 배포
# DBMS_HOST = 'localhost'

DBMS = 'POSTGRESQL'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': DBMS_HOST,
        'NAME':'plant_i',
        'USER': 'plant_i',
        'PASSWORD' : 'plant_i',
        'PORT' : 5432
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'ko-KR'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_L10N = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'
# STATIC_ROOT = posixpath.join(*(BASE_DIR.split(os.path.sep) + ['static']))
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')  # 정적 파일을 모아둘 실제 경로 , POSIX 스타일 경로는 주로 리눅스 및 macOS 환경에서 사용됩니다.

# 개발 중 정적 파일을 찾을 추가 디렉터리 설정
#STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

USE_MOBILE_LOGIN = False

MOSQUITTO_HOST = 'localhost'
MOSQUITTO_WEBSOCKET_PORT =9001
TOPIC_SYSTEM_EVENT='qmlims_system_event'
USE_SYSTEM_EVENT = True 

SITE_NAME = 'hlklemove'

TOPIC_DEVICE_DATA = SITE_NAME + '_device_data'
TOPIC_DEVICE_EVENT = SITE_NAME + '_device_event'
TOPIC_HMI_DATA = SITE_NAME + '_hmi_data'

HMI_RUNNING_MODE = 'mqtt' # mqtt or database

X_FRAME_OPTIONS = 'SAMEORIGIN'#Iframe 오류 관련 수정

folders = []

FILE_UPLOAD_PATH = 'c:\\temp\\plant_i\\'     #업로드한 파일의 영구저장 장소
EXTRA_CODE_PATH = 'c:\\temp\\plant_i\\extra\\' # 사용자 정의 코드의 저장 장소

folders.append(FILE_UPLOAD_PATH)
folders.append(EXTRA_CODE_PATH)

SF_LOG_KEY = ''

for folder in folders:
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except Exception as e:
            pass