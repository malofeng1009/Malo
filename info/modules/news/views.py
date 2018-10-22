from flask import render_template, current_app, session

from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, Category, User
from info.modules.news import news_blu


@news_blu.route('/<int:news_id>')
def news_blu(news_id):
    '''
    新闻详情页
    :param news_id:
    :return:

    '''
    # 查询用户登录信息
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
    data ={
        'user': user.to_dict() if user else None,
        'news_dict_li': news_dict_li,
    }
    return render_template('news/detail.html', data=data)