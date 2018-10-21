import logging
from redis import StrictRedis


class Config(object):
    '''项目的配置'''

    SECRET_KEY = 'iY3RJqHa9Axold8STiZMHzFKmqTJZj5eoTYGFvErS02Ys/WUGfMTbXfUM9DuXUbN'

    # 为mysql添加配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 在请求结束前。如果指定次配置为 True， 那么SQLAlchemy  会自动执行一次 db.session.commit()
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # reids的配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # Session保存配置
    SESSION_TYPE = 'redis'  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 开启 session 签名
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 84600 * 2  # session 的有效期，单位是秒

    # 设置日志等级
    LOG_LEVEL = logging.DEBUG


class DevelopmentConfig(Config):
    '''开发环境下的配置'''
    DEBUG = True


class ProductionConfig(Config):
    '''生产环境下的配置'''
    DEBUG = False
    LOG_LEVEL = logging.WARNING


class TestingConfig(Config):
    '''测试环境下的配置'''
    DEBUG = True

    TESTING = True


Config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
