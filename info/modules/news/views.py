from flask import render_template, current_app, session, g, abort, request, jsonify

from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, Category, User, Comment
from info.modules.news import news_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET


@news_blu.route('/news_collect', methods=['POST'])
@user_login_data
def collect_news():
    '''
    收藏新闻
    1.接收参数
    2.判断参数
    3.查询新闻，并判断新闻是否存在
    4.收藏取消收藏
    :return:
    '''
    user = g.user
    if not user:
        return jsonify(error=RET.SESSIONERR, errmsg='用户未登录')
    # 1.接收参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    # 2.判断参数
    if not  news_id:
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')

    if action not in ['collect', 'cancel_collect']:
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')

    # 3.查询新闻，并判断新闻是否存在
    try:
        news= News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='数据查询错误')
    if not news:
        return jsonify(error=RET.NODATA, errmsg='未查询到新闻数据')

    if action =='cancel_collect':
        # 4.收藏取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)
    else:
        if news not in user.collection_news:
            # 添加到用户的新闻收藏列表
            user.collection_news.append(news)

        return jsonify(error=RET.OK, errmsg='操作成功')






@news_blu.route('/<int:news_id>')
@user_login_data
def news_blu(news_id):
    '''
    新闻详情页
    :param news_id:
    :return:

    '''
    # 查询用户登录信息
    user = g.user
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


    # 查询新闻数据
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not  news:
        abort(404)

    # 更新新闻的点击次数
    news.clicks += 1

    is_collected = False

    if user:
        # 判断用户是否收藏当前新闻，如果收藏：
        # collection_news 后面可以不用加 all， 因为sqlalchemy 会在使用的时候去自动加载
        if news in user.collection_news:
            is_collected = True

    # 查询评论数据
    comments =[]
    try:
         comments = Comment.query.fliter(Comment.news_id==news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    comment_dict_li = []

    for comment in comments:
        comment_dict = comment.to_dict()
        comment_dict_li.append(comment_dict)

    data ={
        'user': user.to_dict() if user else None,
        'news_dict_li': news_dict_li,
        'news':news.to_dict(),
        'is_collected': is_collected,
        'comments':comment_dict_li
    }
    return render_template('news/detail.html', data=data)
