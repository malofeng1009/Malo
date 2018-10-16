import redis
from flask_script import Manager
from flask_wtf.csrf import CSRFProtect
from redis import StrictRedis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# 可以用来指定 session 保存的位置
from flask_session import Session

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
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT )  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 84600 * 2 # session 的有效期，单位是秒

app = Flask(__name__)

# 加载配置
app.config.from_object(Config)

# 初始化数据库
db = SQLAlchemy(app)

redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
#开启当前项目 CSRF 保护
CSRFProtect(app)

Session(app)

manager = Manager(app)
@app.route('/')
def index():
    return 'index'


if __name__ == '__main__':
    manager.run()
