from flask import render_template, g, jsonify, redirect, request, current_app, session
from info import db, constants
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET



@profile_blu.route('/pass_info', method=['POST', 'GET'])
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
    if not all[( old_password,new_password)]:
        return  jsonify(error=RET.PARAMERR, errmsg='参数错误')

    # 判断旧密码是否是正确
    user = g.user
    if user.check_password(old_password):
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
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.THIRDERR, errmsg='上传头像失败')

    # 3.保存头像地址
    user.avatar_url = key
    return jsonify(error=RET.OK, errmsg='OK', data={'avatar_url':constants.QINIU_DOMIN_PREFIX + key})

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

    return  render_template('news/user.html', data={'user': g.user.to_dict()})


