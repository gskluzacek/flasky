import os
import base64
basedir = os.path.abspath(os.path.dirname(__file__))

# decode and return the base64 string if not None or the empty string else return the default value
def base64_decode(base64_val, default_val):
    ret_val = default_val
    if base64_val:
        ret_val = base64.b64decode(bytes(base64_val, "utf-8"))
    return ret_val

class Config:
    SECRET_KEY = base64_decode(os.environ.get('SECRET_KEY'), 'hard to guess string')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = (os.environ.get('MAIL_USE_TLS') == 'Y')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = os.environ.get('FLASKY_MAIL_SENDER')
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30
    APP_DB_USER = os.environ.get('APP_DB_USER') or 'root'
    APP_DB_PASSWORD = os.environ.get('APP_DB_PASSWORD') or 'root'

    @staticmethod
    def init_app(app):
        pass


class DevLocalConfig(Config):
    DEBUG = True
    APP_DB_HOST = 'localhost'
    APP_DB_DATABASE ='komic_logr'
    SQLALCHEMY_ECHO=False
    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://{user}:{password}@{host}/{db}'.format(
        user=Config.APP_DB_USER, password=Config.APP_DB_PASSWORD, host=APP_DB_HOST, db=APP_DB_DATABASE
    )


class DevHostedConfig(Config):
    DEBUG = True
    APP_DB_HOST = 'mysql.komiclogr-dev.komicbox.com'
    APP_DB_DATABASE ='komiclogr_dev'
    SQLALCHEMY_ECHO=False
    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://{user}:{password}@{host}/{db}'.format(
        user=Config.APP_DB_USER, password=Config.APP_DB_PASSWORD, host=APP_DB_HOST, db=APP_DB_DATABASE
    )
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    #    'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    APP_DB_HOST = 'localhost'
    APP_DB_DATABASE ='komic_logr'
    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://{user}:{password}@{host}/{db}'.format(
        user=Config.APP_DB_USER, password=Config.APP_DB_PASSWORD, host=APP_DB_HOST, db=APP_DB_DATABASE
    )
    # SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
    #    'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    APP_DB_HOST = 'localhost'
    APP_DB_DATABASE ='komic_logr'
    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://{user}:{password}@{host}/{db}'.format(
        user=Config.APP_DB_USER, password=Config.APP_DB_PASSWORD, host=APP_DB_HOST, db=APP_DB_DATABASE
    )
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #    'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'dev-local': DevLocalConfig,
    'dev-hosted': DevHostedConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevLocalConfig
}
