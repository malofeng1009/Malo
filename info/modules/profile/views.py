from flask import render_template, g, jsonify, redirect, request, current_app, session, abort
from info import db, constants
from info.models import Category, News, User
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET


@profile_blu.route('/other_news_list')
def other_news_list():
    '''
    返回指定用户发布的新闻
    :return:
    '''
    # 1.取参数
    other_id = request.args.get('user_id')
    page = request.args.get('p', 1)
    # 2.判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')

    try:
        other = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DATAEXIST, errmsg='数据查询失败')

    if not other:
        return jsonify(error=RET.NODATA, errmsg='当前用户不存在')


    try:
        paginate = other.news_list.paginate(page, constants.USER_COLLECTION_MAX_NEWS,False)
        # 获取当前页数据
        news_li = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='数据查询失败')

    news_dict_li = []
    for news_item in news_li:
        news_dict_li.append(news_item.to_basic_dict())

    data = {
        'news_list' : news_dict_li,
        'current_page' : current_app,
        'total_page' : total_page
    }

    return jsonify(error=RET.OK, errmsg='OK', data=data)

@profile_blu.route('/other_info')
@user_login_data
def other_info():
    '''
    其他用户页面
    :return:
    '''
    user = g.user
    # 去查询其他人的用户信息
    other_id = request.args.get('user_id')

    if not other_id:
        abort(404)

    # 查询指定 id 的用户信息
    try:
        other = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)

    if not other:
        abort(404)

    is_followed = False
    # if 当前新闻有作者， 并且 当前登录用户已关注过这个用户
    if other and user:
        # if user 是否关注过 news.user
        if other in user.followed:
            is_followed = True

    data = {
        'is_followed' : is_followed,
        'user' : g.user.to_dict() if g.user else None,
        'other)info' : other.to_dict()
    }

    return render_template('news/other.html', data=data)

@profile_blu.route('/user_follow')
@user_login_data
def user_follow():
    '''
    我的关注
    :return:
    '''
    # 获取页数
    p = request.args.get('p', 1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1
    #取到当前用户
    user = g.user

    follows = []
    current_page = 1
    total_page = 1
    try:
        paginate = user.followed.paginate(p, constants.USER_FOLLOWED_MAX_COUNT, False)
        # 获取当前页数据
        follows =paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    user_dict_li =[]

    for follow_user in follows:
        user_dict_li.append(follow_user.to_dict())

    data = {
        'users' : user_dict_li,
        'current_page' : current_page,
        'total_page' : total_page
    }

    return render_template('news/user_follow.html', data=data)

@profile_blu.route('/news_list', methods=['POST', 'GET'])
@user_login_data
def news_list():
    '''
    用户新闻列表
    :return:
    '''
    # 获取参数
    page = request.args.get('p', 1)
    # 判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    user = g.user
    news_list = []
    current_page = 1
    total_page = 1

    try:
        paginate = News.query.filter(News.user_id==user.id).paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_review_dict())
    data = {
        'news_list': news_dict_li,
        'total_page' : total_page,
        'current_page' : current_page

    }
    return render_template('news/user_news_list.html', data=data    )

@profile_blu.route('/news_release', methods=['POST', 'GET'])
@user_login_data
def news_release():
    '''
    用户新闻发布
    :return:
    '''
    if request.method == 'GET':
        # 加载新闻分类
        categories = []
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
        category_dict_li = []
        for category in categories:
            category_dict_li.append(category.to_dict())
        # 移除最新的分类
        category_dict_li.pop(0)

        return render_template('news/user_news_release.html', data={'categories': category_dict_li})

    # 1.获取要提交的数据
    # 标题
    title = request.form.get('title')
    # 新闻来源
    source = '个人发布'
    # 摘要
    digest = request.form.get('digest')
    # 新闻内容
    content = request.form.get('content')
    # 索引图片
    index_image = request.files.get('index_image')
    # 分类id
    category_id = request.form.get('category_id')

    # 校验参数
    # 2.1 判断数据是否有值
    if not all([title, source, digest, category_id, index_image, content]):
        return jsonify(error=RET.PWDERR, errmsg='参数错误')
    # 2.2
    try:
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')

    # 3. 取到图片，将图片上传到七牛云
    try:
        index_image_data = index_image.read()
        key = storage(index_image_data)
        # 上传到七牛云
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='参数有误')

    news = News()
    news.title = title
    news.digest = digest
    news.source = source
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.content = content
    news.category_id = category_id
    news.user_id = g.user.id
    # 1代表审核状态
    news.status = 1

    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error=RET.DBERR, errmsg='数据保存失败')
    return jsonify(error=RET.OK, errmsg='OK')

@profile_blu.route('/collection', methods=['POST', 'GET'])
@user_login_data
def user_collection():
    '''
    用户新闻收藏
    :return:
    '''
    # 获取参数
    page = request.args.get('p',1)
    # 判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    # 查询用户指定页数的收藏新闻
    user =g.user
    news_list = []
    total_page = 1
    current_page = 1
    try:
        paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        current_page = paginate.page
        total_page = paginate.pages
        news_list = paginate.items
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        'current_page' : current_page,
        'total_page' : total_page,
        "collections" : news_dict_li
    }
    return render_template('news/user_collection.html', data = data)

@profile_blu.route('/pass_info', methods=['POST', 'GET'])
@user_login_data
def pass_info():
    '''
    修改密码
    :return:
    '''
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')

    # 获取参数
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')

    # 校验参数
    if not all([old_password,new_password]):
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')

    # 判断旧密码是否是正确
    user = g.user
    if not user.check_password(old_password):
        return jsonify(error=RET.PWDERR, errmsg='原密码错误')

    # 设置新密码
    user.password = new_password
    return jsonify(error=RET.OK, errms='保存成功')

@profile_blu.route('/pic_info', methods=['POST', 'GET'])
@user_login_data
def pic_info():
    '''
    用户上传头像
    :return:
    '''
    user =g.user
    if request.method == 'GET':
        return render_template('news/user_pic_info.html', data={'user': user.to_dict()})

    # 如果是 post 表示上传图片
    # 1. 取到上传的图片
    try:
        avatar = request.files.get('avatar').read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')

    # 2.上传头像
    try:
        key = storage(avatar)
        print(key)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.THIRDERR, errmsg='上传头像失败')

    # 3.保存头像地址
    user.avatar_url = key

    return jsonify(error=RET.OK, errmsg='OK', data = {'user':user.to_dict() if user else None})

@profile_blu.route('/base_info', methods=['POST', 'GET'])
@user_login_data
def base_info():
    '''
    用户的基本信息
    :return:
    '''
    # 不同的请求方式，做不同的事情
    if request.method == 'GET':
        return render_template('news/user_base_info.html', data={'user': g.user.to_dict()})

    # 代表是修改用户的数据
    # 取到传入的参数
    nick_name = request.json.get('nick_name')
    signature = request.json.get('signature')
    gender = request.json.get('gender')

    # 校验参数
    if not all([nick_name, signature, gender]):
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')

    if gender not in (['WOMAN', 'MAN']):
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')

    # 更新并保存数据
    user = g.user
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender

    return jsonify(error=RET.OK, errmg='ok')

@profile_blu.route('/info')
@user_login_data
def user_info():

    user = g.user
    if not user:
        # 代表没有登录，重定向到首页
        return redirect('/')

    return render_template('news/user.html', data={'user': g.user.to_dict()})


