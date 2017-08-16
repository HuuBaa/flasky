import os
basedir=os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY='huu cool'
    FLASK_MAIL_SUBJECT_PREFIX='[Flasky]'
    FLASK_MAIL_SENDER='Huu Flask <742790905@qq.com>'
    FLASKY_ADMIN=os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    MAIL_SERVER='smtp.qq.com'
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir,'data-develop.sqlite')

class TestingConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir,'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir,'data.sqlite')

config={
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}
