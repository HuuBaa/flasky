import os
basedir=os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY='huu cool'
    # SSL_DISABLE = True
    FLASK_MAIL_SUBJECT_PREFIX='[Flasky]'
    FLASK_MAIL_SENDER='Huu Flask <742790905@qq.com>'
    FLASKY_ADMIN=os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    MAIL_SERVER='smtp.qq.com'
    MAIL_PORT=587   
    MAIL_USE_TLS = True
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
    SQLALCHEMY_DATABASE_URI=os.environ.get('DEV_DATABASE_URL') or'sqlite:///' + os.path.join(basedir,'data-develop.sqlite')

    

class TestingConfig(Config):
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    WTF_CSRF_ENABLED=False
    TESTING=True
    SQLALCHEMY_DATABASE_URI=os.environ.get('TEST_DATABASE_URL') or'sqlite:///' + os.path.join(basedir,'data-test.sqlite')



class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,'data.sqlite')

    @classmethod
    def init_app(cls,app):
        Config.init_app(app)

        import logging
        from logging.handlers import SMTPHandler
        credentials=None
        secure=None
        if getattr(cls,'MAIL_USERNAME',None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls,'MAIL_USE_TLS',None):
                secure=()
        mail_handler=SMTPHandler(
            mailhost=('smtp.qq.com',587),
            fromaddr=cls.FLASK_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASK_MAIL_SUBJECT_PREFIX+' Application Error',
            credentials=credentials,
            secure=secure
            )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        import logging
        from logging import StreamHandler
        file_handler=SMTPHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

config={
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig,
    'heroku':HerokuConfig
}
