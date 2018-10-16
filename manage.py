from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_wtf.csrf import CSRFProtect
from redis import StrictRedis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# 可以用来指定 session 保存的位置
from flask_session import Session
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

manager = Manager(app)
# 将 app 与 db 关联
Migrate(app, db)
# 将迁移命令添加到 manager 中
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    return 'index'


if __name__ == '__main__':
    manager.run()
