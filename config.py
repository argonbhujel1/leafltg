import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'leaf_letang.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')

    # Company configuration — only verified / placeholder fields
    COMPANY_NAME = 'Leaf Letang Enterprises'
    COMPANY_TAGLINE = 'From Local Leaves to Sustainable Value.'
    COMPANY_LOCATION = 'Letang Municipality, Morang, Koshi Province, Nepal'
    COMPANY_ADDRESS_LINE1 = 'Letang Municipality'
    COMPANY_ADDRESS_LINE2 = 'Morang, Koshi Province'
    COMPANY_ADDRESS_LINE3 = 'Nepal'
    COMPANY_PHONE = os.environ.get('COMPANY_PHONE') or ''
    COMPANY_EMAIL = os.environ.get('COMPANY_EMAIL') or ''
    COMPANY_FACEBOOK = os.environ.get('COMPANY_FACEBOOK') or ''
    COMPANY_INSTAGRAM = os.environ.get('COMPANY_INSTAGRAM') or ''
    COMPANY_YOUTUBE = os.environ.get('COMPANY_YOUTUBE') or ''
    COMPANY_TIKTOK = os.environ.get('COMPANY_TIKTOK') or ''
    COMPANY_WEBSITE = os.environ.get('COMPANY_WEBSITE') or 'https://leafletang.com'

    # Production started
    PRODUCTION_STARTED = 'November 2021'
    ESTABLISHED_YEAR_BS = '2078'
    INITIAL_INVESTMENT = 'Approximately NPR 2.1 million'
    HISTORICAL_PRODUCTION = 'Approximately 10,000 pieces per day (historical reported figure)'

    # Uploads (gallery images) — works from PC and phone file pickers
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images', 'gallery')
    HERO_UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images', 'hero')
    FOUNDERS_UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images', 'founders')
    PRODUCTS_UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images', 'products')
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
