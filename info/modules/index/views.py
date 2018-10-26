from flask import render_template, current_app, session, request, jsonify
# from info import redis_store
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import User, News, Category
from info.utils.response_code import RET
from . import index_blu


@index_blu.route('/news_list')
def news_list():
    '''
    获取首页新闻数据
    :return:
    '''
    # 1.获取参数
    # 新闻的分类id
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')
    # 2.校验参数
    try:
        page = int(page)
        cid = int(cid)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')

    filters = [News.status == 0]
    if cid != 1: # 查询的不是最新的数据
        # 需要添加条件
        filters.append(News.category_id == cid)
    # 3.查询数据
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='数据查询错误')
    # 取到当前页的数据
    news_model_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page
    # 将模型对象列表转换成字典
    new_dict_li = []
    for news in news_model_list:
        new_dict_li.append(news.to_basic_dict())


    data = {
        'total_page':total_page,
        'current_page':current_page,
        'news_dict_li': new_dict_li,
    }
    return jsonify(error=RET.OK, errmsg='ok', data = data)


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
        news_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    # 定义一个空的字典列表，里面装的就是字典
    news_dict_li = []
    # 遍历对象列表，将对象的字典添加到字典列表当中
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())
    # 查询分类数据，通过模板的形式渲染出来
    categories= Category.query.all()

    category_li = []
    for category in categories:
        category_li.append(category.to_dict())

    # print(user.to_dict())
    data = {
        'user': user.to_dict() if user else None,
        'news_dict_li': news_dict_li,
        'category_li': category_li
    }
    return render_template('news/index.html', data=data)


# 在打开网页的时候，浏览器会默认请求根路径 + favicon.ico 作为网站标签的小图标
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
