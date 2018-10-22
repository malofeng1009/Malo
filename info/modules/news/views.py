from flask import render_template

from info.modules.news import news_blu


@news_blu.route('/<int:news_id>')
def news_blu(news_id):
    '''
    新闻详情页
    :param news_id:
    :return:
    '''

    return render_template('news/detail.html')
