# EnPluzz
# Copyright (C) 2025  Elioty <roadkiller.cl@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Django settings for enpluzz project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
from enpluzz_core.enpLangDict import ENPLangDict
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# For production purpose, a secret key can be generated with the following command:
# python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY = ''

SECRET_KEY_FALLBACKS = [
]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INTERNAL_IPS = [
    "127.0.0.1",
]

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'enpluzz_core.apps.EnpluzzCoreConfig',
    'enpluzz_items.apps.EnpluzzItemsConfig',
    'enpluzz_heroes.apps.EnpluzzHeroesConfig',
    'enpluzz_troops.apps.EnpluzzTroopsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar', # For debug purposes only
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware', # For debug purposes only
]

ROOT_URLCONF = 'enpluzz.urls'

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

WSGI_APPLICATION = 'enpluzz.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    ('game_assets', (BASE_DIR / 'enpluzz_core' / 'game_data' / 'assets_extract').as_posix()),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CLASSES_TO_IMPORT_FROM_GAME_CONFIGURATION = [
    'enpluzz_heroes.models.Family',
    'enpluzz_heroes.models.FamilySet',
    'enpluzz_heroes.models.ClassType',
    'enpluzz_heroes.models.ManaSpeed',
    'enpluzz_heroes.models.CostumeBonus',
    'enpluzz_heroes.models.AetherGifts',
    'enpluzz_heroes.models.SpecialSkill',
    'enpluzz_heroes.models.Hero',
    'enpluzz_items.models.Item',
]

ENP_LANGUAGES = dict()
ENP_SETTINGS = dict()
__game_data_path = BASE_DIR / 'enpluzz_core' / 'game_data'
if __game_data_path.is_dir(): # It might not exist if no game data archive has been imported yet
    __lang_path = __game_data_path / 'languages'
    with open(__game_data_path / 'cached_configurations' / 'languageOverrides.json', mode='r', encoding='UTF-8') as fd:
        __overrides_configuration = json.load(fd)
    for __lang in ('English', 'French', 'Spanish', 'Italian', 'German', 'Japanese', 'Korean'):
        ENP_LANGUAGES[__lang] = ENPLangDict(__lang, __lang_path, __overrides_configuration)
    del __lang, __lang_path, __overrides_configuration
    with open(__game_data_path / 'game_settings.json', encoding='UTF-8') as fd:
        ENP_SETTINGS = json.load(fd)
del __game_data_path
