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
    FLASKY_POST_PER_PAGE=10
    FLASKY_COMMENT_PER_PAGE=8
    SQLALCHEMY_RECORD_QUERIES=True
    FLASK_SLOW_DB_QUERY_TIME=0.5

    @classmethod
    def init_app(cls,app):
        pass

class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir,'data-develop.sqlite')


class TestingConfig(Config):
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    WTF_CSRF_ENABLED=False
    TESTING=True
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir,'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir,'data.sqlite')

    @classmethod
    def init_app(cls,app):
        Config.init_app(app)

        import logging
        from logging.handlers import SMTPHandler
        credentials=None
        secure=None
        if getattr(cls,'MAIL_USERNAME',None) is not None:
            credentials=(cls.MAIL_USERNAME,cls.MAIL_PASSWORD)
            if getattr(cls,'MAIL_USE_SSL',None):
                secure=()
        mail_handler=SMTPHandler(
            mailhost=('smtp.qq.com',587),
            fromaddr=cls.FLASK_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASK_MAIL_SUBJECT_PREFIX+' Application Error',
            credentials=credentials,
            secure=secure
            )
        mail_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(mail_handler)


config={
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}
