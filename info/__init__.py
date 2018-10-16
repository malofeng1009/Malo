from flask import Flask
# 可以用来指定 session 保存的位置
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import Config

# 初始化数据库
db = SQLAlchemy()
redis_store = None

def create_app(config_name):
    '''通过传入不同配置名i，初始化器对应配置的应用实例'''
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(Config[config_name])

    # 配置数据库
    db.init_app(app)

    # 配置redis
    global redis_store
    redis_store = StrictRedis(host=Config[config_name].REDIS_HOST, port=Config[config_name].REDIS_PORT)
    # 开启当前项目 CSRF 保护
    CSRFProtect(app)

    Session(app)

    return app


