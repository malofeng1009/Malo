from flask_wtf.csrf import CSRFProtect
from redis import StrictRedis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    DEBUG = True

    # 为mysql添加配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/Information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # reids的配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379


app = Flask(__name__)

# 加载配置
app.config.from_object(Config)

# 初始化数据库
db = SQLAlchemy(app)

redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
#开启当前项目 CSRF 保护
CSRFProtect(app)

@app.route('/')
def index():
    return 'index'


if __name__ == '__main__':
    app.run(debug=True)
