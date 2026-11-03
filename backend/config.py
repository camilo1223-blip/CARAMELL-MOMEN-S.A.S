import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-this-secret-key')
    ADMIN_REGISTRATION_KEY = os.environ.get('ADMIN_REGISTRATION_KEY', 'dev-only-change-admin-key')

    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'caramell_momen_db')

    # En Vercel el disco local es temporal. Para persistencia real configura
    # DATABASE_URL con PostgreSQL o MySQL alojado externamente.
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
    elif database_url and database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)

    if database_url:
        SQLALCHEMY_DATABASE_URI = database_url
    elif os.environ.get('VERCEL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/caramell_momen.db'
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'caramell_momen.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')

    STORE_NAME = 'CARAMELL MOMEN S.A.S.'
    STORE_CURRENCY = 'COP'
    STORE_CONTACT_EMAIL = 'contacto@caramellmomen.com'
    STORE_CONTACT_PHONE = '+57 (601) 895-4321'
    STORE_HOURS = 'Lunes a Sábado: 8:00 AM - 7:00 PM'
