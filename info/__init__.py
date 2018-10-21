from logging.handlers import RotatingFileHandler
import logging
from flask import Flask
# 可以用来指定 session 保存的位置
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from redis import StrictRedis
from config import Config
# 初始化数据库
# 在 flask 很多扩展里面都可以先初始化扩展的对象然后去调用 init_app 方法去初始化
from info.utils.common import do_index_class

db = SQLAlchemy()
redis_store = None  # type: StrictRedis


def setup_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=Config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    '''通过传入不同配置名i，初始化器对应配置的应用实例'''
    #  配置日志,并且传入配置名字，以便获取到指定配置所对应的日志等级
    setup_log(config_name)
    # 创建 Flask 对象
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(Config[config_name])
    # 配置数据库
    db.init_app(app)
    # 配置redis
    global redis_store
    redis_store = StrictRedis(host=Config[config_name].REDIS_HOST, port=Config[config_name].REDIS_PORT, decode_responses=True)
    # 开启当前项目 CSRF 保护,制作服务器验证功能
    # 帮我们做了：从 cookie 中取出随机值，从表单中取出随机值，然后进行校验，并且响应校验结果
    # 我们需要做：1.在界面加载的时候，往 cookie 中添加一个csrf_token 并且在表单中添加一个隐藏的csrf_token
    CSRFProtect(app)
    # 设置session的保存位置
    Session(app)

    @app.after_request
    def after_request(response):
        # 生成一个随机的 csrf_token 的值
        csrf_token= generate_csrf()
        # 设置一个 cookie
        response.set_cookie('csrf_token', csrf_token)
        return  response
    # 添加模板过滤器
    app.add_template_filter(do_index_class,'index_class')
    # 注册蓝图

    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    return app
