from flask import render_template, current_app, session
# from info import redis_store
from info.models import User, News
from . import index_blu

@index_blu.route('/')
def index():
    # session['name'] = 'itheima'

    # 测试打印日志

    # current_app.logger.debug('测试debug')
    # current_app.logger.error('测试error')
    # current_app.logger.fatal('测试fatal')

    # 向 redis 中保存一个字 name itcast
    # 获取当前用户登陆的信息
    # 显示用户是否登录的逻辑
    user_id = session.get('user_id', None)
    # 通过id获取当前用户的信息
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 右侧新闻排行的逻辑
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(10)
    except Exception as e:
        current_app.logger.error(e)
    # 定义一个空的字典列表，里面装的就是字典
    news_dict_li = []
    # 遍历对象列表，将对象的字典添加到字典列表当中
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())
    # 查询分类数据，通过模板的形式渲染出来

    data = {
        'user': user.to_dict() if user else None,
        'news_dict_li': news_dict_li
    }
    return render_template('news/index.html', data=data)
# 在打开网页的时候，浏览器会默认请求根路径 + favicon.ico 作为网站标签的小图标
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
