from flask import render_template, request, session, redirect, url_for, jsonify, g

from info.models import User
from info.modules.admin import admin_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET


@admin_blu.route('/logout')
@user_login_data
def logout():
    '''
    退出登录
    :return:
    '''
    session.pop('user_id', None)
    session.pop('mobile', None)
    session.pop('nick_name', None)
    session.pop('is_admin', None)

    return jsonify(error=RET.OK, errmsg='退出成功')

@admin_blu.route('/index', methods=['POST','GET'])
@user_login_data
def index():
    '''
    管理后台主页
    :return:
    '''
    user = g.user
    return render_template('admin/index.html', user=user.to_dict())

@admin_blu.route('/login', methods=['POST', 'GET'])
@user_login_data
def login():
    '''
    后台管理员登录
    :return:
    '''
    if  request.method == 'GET':
        # 判断当前是否有登陆， 如果有登录直接重定向到管理员后台主页
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        if user_id and is_admin:
            return render_template('admin/index.html')

        return render_template('admin/login.html')

    # 取到登录的参数
    username = request.form.get('username')
    password = request.form.get('password')
    # 判断参数
    if not all([username, password]):
        return render_template('admin/login.html', errmsg='参数错误')
    # 查询当前用户
    try:
        user = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except Exception as e:
        return render_template('admin/login.html', errmsg='用户信息查询失败')

    if not user:
        return render_template('admin/login.html', errmsg='未查到用户信息')

    # 检验密码
    if not user.check_password(password):
        return render_template('admin/login.html', errmsg='用户名或密码错误')

    # 保存用户的登录信息
    session['user_id'] = user.id
    session['mobile']  = user.mobile
    session['nick_name'] = user.nick_name
    session['is_admin'] = user.is_admin

    # 跳转到后台管理页面
    return render_template('admin/index.html')