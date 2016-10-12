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
    'assets',
    'utils',
    'bootstrapform',
    'registration',
    'django_tables2',
    'inplaceeditform_bootstrap',  # it is very important that this app is before that inplaceeditform and inplaceeditform_extra_fields
    'inplaceeditform',
    'inplaceeditform_extra_fields',  # this is optional but recommended
    'bootstrap3_datetime', # this is optional but recommended
    'django_crontab',
    'tagging',
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

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'internalerpdb',
        'USER': 'embeduradmin',
        'PASSWORD': 'Christy94538',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'guardian.backends.ObjectPermissionBackend',
)

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

CRONJOBS = [
    ('0 15 * * *', 'utils.cron.SendLeavesToApproveEmail', '>> /tmp/scheduled_job.log')
]

# Deployment

DEPLOYMENT_PORTAL_URL = "http://61.16.140.205:2401/"

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
DEFAULT_CC_EMAIL = 'noreply@embedur.com'
DEFAULT_LEAVES_EMAIL = 'HRIndia@embedur.com'

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.
REGISTRATION_AUTO_LOGIN = True # Automatically log the user in.
#REGISTRATION_EMAIL_HTML = True
REGISTRATION_DEFAULT_FROM_EMAIL = 'noreply@embedur.com'
LOGIN_REDIRECT_URL = '/hr/empInfo/'  # The page you want users to arrive at after they successful log in
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

#DJANGO-TAGGING
#FORCE_LOWERCASE_TAGS = True

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

# INPLACE-EDIT Module related
# Optional, but recommended
ADAPTOR_INPLACEEDIT = {}
if 'inplaceeditform_extra_fields' in INSTALLED_APPS:
    ADAPTOR_INPLACEEDIT['tiny'] = 'inplaceeditform_extra_fields.fields.AdaptorTinyMCEField'
    # You can add the other adaptors of inplaceeditform_extra_fields
    # https://pypi.python.org/pypi/django-inplaceedit-extra-fields#installation
if 'bootstrap3_datetime' in INSTALLED_APPS:
    ADAPTOR_INPLACEEDIT['date'] = 'inplaceeditform_bootstrap.fields.AdaptorDateBootStrapField'
    ADAPTOR_INPLACEEDIT['datetime'] = 'inplaceeditform_bootstrap.fields.AdaptorDateTimeBootStrapField'

INPLACEEDIT_EDIT_TOOLTIP_TEXT = 'Please doubleclick to edit'
INPLACEEDIT_EDIT_EMPTY_VALUE = 'Double click to edit'
INPLACEEDIT_AUTO_SAVE = True
INPLACEEDIT_EVENT = "dblclick"
INPLACEEDIT_DISABLE_CLICK = True  # For inplace edit text into a link tag
INPLACEEDIT_EDIT_MESSAGE_TRANSLATION = 'Write a translation' # transmeta option
INPLACEEDIT_SUCCESS_TEXT = 'Successfully saved'
INPLACEEDIT_UNSAVED_TEXT = 'You have unsaved changes'
INPLACE_ENABLE_CLASS = 'enable'
DEFAULT_INPLACE_EDIT_OPTIONS = {} # dictionnary of the optionals parameters that the templatetag can receive to change its behavior (see the Advanced usage section)
DEFAULT_INPLACE_EDIT_OPTIONS_ONE_BY_ONE = True # modify the behavior of the DEFAULT_INPLACE_EDIT_OPTIONS usage, if True then it use the default values not specified in your template, if False it uses these options only when the dictionnary is empty (when you do put any options in your template)
ADAPTOR_INPLACEEDIT_EDIT = 'hr.perms.MyAdaptorEditInline' # Explain in Permission Adaptor API
#ADAPTOR_INPLACEEDIT = {'myadaptor': 'app_name.fields.MyAdaptor'} # Explain in Adaptor API
INPLACE_GET_FIELD_URL = None # to change the url where django-inplaceedit use to get a field
INPLACE_SAVE_URL = None # to change the url where django-inplaceedit use to save a field

# GUARDIAN App specific
ANONYMOUS_USER_ID = -1

# HR APP SPECIFIC settings ####
MAIL_ENABLE = True

DEFAULT_USER_ACCOUNT_PASSWD = "Christy94538"

USER_GROUP_CHOICES = (
    ('EMPLOYEE', 'Employee'),
    ('MANAGER', 'Manager'),
    ('HR-MANAGER', 'HR Manager'),
    ('HR-EXECUTIVE', 'HR Executive'),
)

DEFAULT_USER_GROUP_CHOICE = 'EMPLOYEE'

# TODO: Modify this value in future according to CSS Bootstrap value in UI
DEFAULT_PAGINATOR_RECORDS_PERPAGE = 6

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

# ASSET MANAGEMENT #
ASSET_PRIVILEGES_CHOICES = (
    ('ASSETS-EMPLOYEE', 'Employee'),
    ('ASSETS-ADMIN', 'Assets-Admin'),
    ('ASSETS-TECHNICIAN', 'Technician'),
    ('ASSETS-VALIDATOR', 'Validator'),
)

DEFAULT_ASSET_PRIVILEGES_CHOICE = 'EMPLOYEE'

ASSET_STATUS_CHOICES = (
    ('INSTOCK', 'In-Stock'),
    ('ASSIGNED', 'Assigned'),
    ('LOST', 'Lost'),
    ('STOLEN', 'Stolen'),
    ('MISSING', 'Missing'),
    ('INSERVICE', 'In-Service'),
    ('REPAIR', 'Repair'),
)

ASSET_DEFAULT_STATUS = 'INSTOCK'

ASSET_ASSIGNMENT_CATEGORY = (
    ('GENERAL', 'General'),
    ('EMPLOYEE', 'Employee'),
    ('MANAGER', 'Manager'),
    ('SHARED', 'Shared'),
)

ASSET_DEFAULT_ASSIGNMENT_CATEGORY = 'GENERAL'

AVAIL_ASSET_STATUS_CHOICES = (
    ('AVAIL', 'Avail'),
    ('APPROVE', 'Approve'),
    ('REJECT', 'Reject'),
    ('RETURNED', 'Returned'),
)

AVAIL_ASSET_STATUS_DEFAULT_CHOICE = 'AVAIL'
