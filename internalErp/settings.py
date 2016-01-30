"""
Django settings for internalErp project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hfj00604xw1q!^o6(jneu#z*bx$1k*g$r&eg44pu_b#gad2p5#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    #'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hr',
    'utils',
    'bootstrapform',
    'registration',
    'django_tables2',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'internalErp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'internalErp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Deployment

EMAIL_HOST = 'remote.embedur.com'
#EMAIL_HOST_USER = 'embedur\\aravindhd'
#EMAIL_HOST_PASSWORD = '$*AXRA2dRT*$'
EMAIL_PORT = 25
EMAIL_USE_TLS = False
'''
#Development
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
'''
DEFAULT_FROM_EMAIL = 'noreply@embedur.com'

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.
REGISTRATION_AUTO_LOGIN = True # Automatically log the user in.
#REGISTRATION_EMAIL_HTML = True
REGISTRATION_DEFAULT_FROM_EMAIL = 'noreply@embedur.com'
LOGIN_REDIRECT_URL = '/hr/'  # The page you want users to arrive at after they successful log in
LOGIN_URL = '/accounts/login/'  # The page users are directed to if they are not logged in, and are trying to access pages requiring authentication

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),

]

MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static_cdn")
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "media_cdn")

# Auto-discovering of application specific settings.
#for app in INSTALLED_APPS:
#    try:
#        prefix, sep, app_name = app.rpartition('.')
#        settings = __import__(app_name, globals(), locals(), ['*'], 1)
#        for attr in dir(settings):
#            if not attr.startswith('_'):
#                globals()[attr] = getattr(settings, attr)
#    except:
#        pass

# HR APP SPECIFIC settings ####
MAIL_ENABLE = True

DEFAULT_USER_ACCOUNT_PASSWD = "Christy94538"

DEFAULT_PAGINATOR_RECORDS_PERPAGE = 10

EMPLOYMENT_TYPE_CHOICES = (
    ('PE', 'Permanent'),
    ('PB', 'Probationary'),
    ('IN', 'Intern'),
    ('CT', 'Contract'),
)

EMPLOYMENT_STATUS_CHOICES = (
    ('HR', 'Hired'),
    ('REHR', 'Re-Hired'),
    ('TERM', 'Terminated'),
    ('RS', 'Resigned'),
    ('SUS', 'Suspended'),
    ('CE', 'Contract Expired'),
    ('LEFT', 'Left'),
)

DEFAULT_EMPLOYMENT_TYPE = 'PE'
DEFAULT_EMPLOYMENT_STATUS = 'HR'

LEAVE_TYPE_CHOICES = (
    ('CL', 'Casual'),
    ('PL', 'Privilege'),
    ('SL', 'Sick'),
    ('WFH', 'Work From Home'),
    ('COMP', 'Compensation'),
    ('LOP', 'Loss Of Pay'),
)

DEFAULT_LEAVE_TYPE = 'PL'

LEAVE_STATUS_CHOICES = (
    ('CREATED', 'Create'),
    ('SUBMITTED', 'Submit'),
    ('APPROVED', 'Approve'),
    ('REJECTED', 'Reject'),
    ('CLOSED', 'Close'),
    ('REOPENED', 'Re-open'),
    ('DISCARD', 'Discard'),
)

LEAVE_DEFAULT_STATUS = 'CREATED'

#WORKING_DAY_START = datetime.time(9, 0)
#WORKING_DAY_END = datetime.time(18, 30)

#LAUNCH_TIME_START = datetime.time(13, 0)
#LAUNCH_TIME_END = datetime.time(14, 30)

#EXPENSE_TYPE_CHOICES = (
#    ('TRV', _('travel')),
#    ('MDC', _('medical')),
#    ('FOD', _('food')),
#    ('CAL', _('call')),
#    ('OTH', _('others')),
#)

#DEFAULT_EXPENSE_TYPE = 'TRV'