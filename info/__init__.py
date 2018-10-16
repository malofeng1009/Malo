from flask import Flask
# 可以用来指定 session 保存的位置
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import Config

app = Flask(__name__)

# 加载配置
app.config.from_object(Config)

# 初始化数据库
db = SQLAlchemy(app)

redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 开启当前项目 CSRF 保护
CSRFProtect(app)

Session(app)
