from flask import render_template, current_app

# from info import redis_store
from . import index_blu


@index_blu.route('/')
def index():
    # session['name'] = 'itheima'

    # 测试打印日志

    # current_app.logger.debug('测试debug')
    # current_app.logger.error('测试error')
    # current_app.logger.fatal('测试fatal')

    # 向 redis 中保存一个字 name itcast
    return render_template('news/index.html')

# 在打开网页的时候，浏览器会默认请求根路径 + favicon.ico 作为网站标签的小图标
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
