from redis import StrictRedis


class Config(object):
    '''项目的配置'''
    DEBUG = True

    SECRET_KEY = 'iY3RJqHa9Axold8STiZMHzFKmqTJZj5eoTYGFvErS02Ys/WUGfMTbXfUM9DuXUbN'

    # 为mysql添加配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/Information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # reids的配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # Session保存配置
    SESSION_TYPE = 'redis'  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 开启 session 签名
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 84600 * 2  # session 的有效期，单位是秒