import time
from datetime import datetime, timedelta
from flask import render_template, request, session, redirect, url_for, jsonify, g, current_app

from info.models import User
from info.modules.admin import admin_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET

@admin_blu.route('/user_count')
@user_login_data
def user_count():
    '''
    用户统计
    :return:
    '''
    # 总人数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 月新增数
    mon_count = 0
    t = time.localtime()
    begin_mon_date_str = '%d-%02d-01' % (t.tm_year, t.tm_mon)
    # 将字符串转成datetime对象
    begin_mon_date = datetime.strptime("2018-08-01", "%Y-%m-%d")
    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time > begin_mon_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 日新增数
    day_count = 0
    begin_day_date = datetime.strptime(('%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > begin_day_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 拆线图数据

    active_time = []
    active_count = []

    # 取到今天的时间字符串
    today_date_str = ('%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday))
    # 转成时间对象
    today_date = datetime.strptime(today_date_str, "%Y-%m-%d")

    for i in range(0, 31):
        # 取到某一天的0点0分
        begin_date = today_date - timedelta(days=i)
        # 取到下一天的0点0分
        end_date = today_date - timedelta(days=(i - 1))
        count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                  User.last_login < end_date).count()
        active_count.append(count)
        active_time.append(begin_date.strftime('%Y-%m-%d'))

    # User.query.filter(User.is_admin == False, User.last_login >= 今天0点0分, User.last_login < 今天24点).count()

    # 反转，让最近的一天显示在最后
    active_time.reverse()
    active_count.reverse()

    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_time": active_time,
        "active_count": active_count
    }

    return render_template('admin/user_count.html', data=data)


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