from flask import render_template, g, jsonify, redirect, request, current_app, session
from info import db
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET


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
    data ={
        'user':user.to_dict()
    }
    return  render_template('news/user.html', data =data)


