from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'user',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_email',
    'corsheaders',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_otp.middleware.OTPMiddleware",
]

ROOT_URLCONF = 'account.urls'

WSGI_APPLICATION = 'account.wsgi.application'

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

WSGI_APPLICATION = 'account.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "account_db",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "db",
        "PORT": "5432",
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',  # SQLite database file located in the base directory
#     }
# }


# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
SECRET_KEY = os.environ.get('SECRET_KEY')

# Custom user model
AUTH_USER_MODEL = 'user.CustomUser'  # Specify the custom user model


OAUTH2_CLIENT_ID = os.environ.get('OAUTH2_CLIENT_ID')
OAUTH2_CLIENT_SECRET = os.environ.get('OAUTH2_CLIENT_SECRET')
OAUTH2_REDIRECT_URI = os.environ.get('OAUTH2_REDIRECT_URI')

OAUTH_URL = os.environ.get('OAUTH_URL')
TOKEN_URL = os.environ.get('TOKEN_URL')
USER_URL = os.environ.get('USER_URL')

#cookie
SECURE_SSL_REDIRECT = False  # ローカル開発環境ではHTTPSリダイレクトは不要
CSRF_COOKIE_SECURE = False  # HTTPS接続がない場合はCSRFクッキーをセキュアにしない
SESSION_COOKIE_SECURE = False  # セッションIDのクッキーをセキュアにしない

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",  # フロントエンドのURL
    "http://127.0.0.1:3000",  # 127.0.0.1 を許可
    "http://localhost:80",  # フロントエンドのURL
    "http://127.0.0.1:80",  # 127.0.0.1 を許可
    "http://localhost",
    "https://localhost",
]

# settings.pyに追加
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # フロントエンドのURL
    "http://127.0.0.1:3000",  # 127.0.0.1 を許可
    "http://localhost:80",  # フロントエンドのURL
    "http://127.0.0.1:80",  # 127.0.0.1 を許可
    "http://localhost",
    "https://localhost",
]

ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1',
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

# settings.py
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'None'  # 開発環境用
CSRF_COOKIE_SAMESITE = 'None'  # 開発環境用
# クッキー関連の設定（特に、クロスオリジンリクエストを扱う場合に重要）

CORS_PREFLIGHT_MAX_AGE = 60 * 30