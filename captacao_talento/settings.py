"""
Django settings for captacao_talento project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

def get_env_var(var):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var]
    except KeyError:
        fstring_error = "{} environment variable is not set!"
        raise ImproperlyConfigured(fstring_error.format(var))


SECRET_KEY = get_env_var('SECRET_KEY')

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
    # third-party
    'django_extensions',
    'widget_tweaks',
    # apps
    'bot',
    'trello_helper',
    'globalvars',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'captacao_talento.urls'

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

WSGI_APPLICATION = 'captacao_talento.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# E-mail variables
EMAIL_HOST = get_env_var('EMAIL_HOST')
EMAIL_PORT = get_env_var('EMAIL_PORT')
EMAIL_HOST_USER = get_env_var('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_var('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = get_env_var('EMAIL_USE_TLS')

# Trello credentials
TRELLO_TOKEN = get_env_var('TRELLO_TOKEN')
TRELLO_KEY = get_env_var('TRELLO_KEY')

# Trello references
SALES_BOARD_ID = get_env_var('SALES_BOARD_ID')
SALES_BOARD_URL = get_env_var('SALES_BOARD_URL')
CONTRACTS_BOARD_ID = get_env_var('CONTRACTS_BOARD_ID')
CONTRACTS_BOARD_URL = get_env_var('CONTRACTS_BOARD_URL')
CONTACTS_TABLE_URL = get_env_var('CONTACTS_TABLE_URL')

# external urls
MANUAL_URL = get_env_var('MANUAL_URL')
PROPOSAL_URL = get_env_var('PROPOSAL_URL')
MEDIA_KIT_URL = get_env_var('MEDIA_KIT_URL')
EMAIL_MODEL_URL = get_env_var('EMAIL_MODEL_URL')
CLOSED_TABLE_URL = get_env_var('CLOSED_TABLE_URL')

# dev contact
CONTACT = get_env_var('CONTACT')
