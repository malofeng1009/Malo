import random
import re
from datetime import datetime

from flask import request, abort, current_app, make_response, jsonify, session
from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import  passport_blu

@passport_blu.route('/logout')
def logout():
    '''
    退出登录
    :return:
    '''
    # pop 是移除 session 中的数据dict
    # pop 会有一个返回值，如果要移除的key不存在，就返回None
    session.pop('user_id', None)
    session.pop('mobile', None)
    session.pop('nick_name', None)
    session.pop('is_admin', None)

    return jsonify(error=RET.OK, errmsg='退出成功')

@passport_blu.route('/login', methods=['POST'])
def login():
    '''
    1.获取参数
    2.校验参数
    3.校验密码是否正确
    4.保存用户登录状态
    5.响应
    :return:
    '''
    # 1.获取参数
    params_dict = request.json

    mobile = params_dict.get('mobile')
    password = params_dict.get('password')

    # 2校验参数
    if not all([mobile, password]):
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')
    # 校验手机号是否正确
    if not re.match('1[3678]\\d{9}', mobile):
        return jsonify(error=RET.PARAMERR, errmsg='手机格式不正确')
    # 3.校验密码是否正确
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='数据查询错误')
    # 判断用户是否存在
    if not user:
        return jsonify(error=RET.NODATA, errmsg='用户不存在')
    # 校验登录密码是否和用户的密码一致
    if not user.check_password(password):
        return jsonify(error=RET.PWDERR, errmsg='用户名或密码错误')
    # 4.保存用户的登录状态
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name
    # 设置当前用户最后一次登录时间
    user.last_login = datetime.now()
    # 如果在视图函数中，对模型身上的属性有修改，那么需要commit提交到数据库
    #　但其实可以自己不用去写，db.session.commit(), 前提是对SQLAchemy有过相关配置
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     current_app.logger.error(e)
    # 5.响应
    return jsonify(error=RET.OK, errmsg='登录成功')

@passport_blu.route('/register', methods=['POST'])
def register():
    '''
    1.获取参数
    2.校验参数
    3.取到服务器的真实短信验证码内容
    4.校验用户输入的短信验证码内容和真实的短信验证码内容是否一致
    5.如果一致，初始化 User 模型并且赋值属性
    6.将 User 模型添加数据库
    7.返回响应
    :return:
    '''

    # 1.获取参数
    param_dict = request.json
    mobile = param_dict.get('mobile')
    smscode = param_dict.get('smscode')
    password = param_dict.get('password')
    # 2.校验参数
    if not all([mobile, smscode, password]):
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')
    if not re.match('1[35678]\\d{9}', mobile):
        return jsonify(error=RET.PARAMERR, errmsg='手机格式不正确')
    # 3.取到服务器的真实短信验证码内容
    try:
        real_sms_code = redis_store.get('SMS_' + mobile)
    except Exception as e:
        current_app.logger(e)
        return jsonify(error=RET.DBERR, errmsg='数据查询失败')
    if not real_sms_code:
        return jsonify(error=RET.NODATA, errmsg='图片验证码已经过期')
    # 4.校验用户输入的短信验证码内容和真实的短信验证码内容是否一致
    if real_sms_code != smscode:
        return jsonify(error=RET.DATAERR, errmsg='验证码错误')
    # 5.如果一致，初始化User模型并且赋值属性
    user = User()
    user.mobile = mobile
    # 展示没有昵称，用手机号替代
    user.nick_name = mobile
    # 记录用户最后一次登录时间
    user.last_login = datetime.now()
    # 对密码做加密处理
    user.password = password
    # 6.将User模型添加数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error=RET.DBERR, errmsg='数据保存失败')

    # 往 session 中保存数据表示当前已经登登录
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name
    # 7.返回响应
    return jsonify(error=RET.OK, errmsg='注册成功')

@passport_blu.route('/sms_code', methods=["POST"])
def send_sms_code():
    '''发送短信验证码的逻辑
        1.获取参数：手机号码、图片验证码内容、图片验证码的编号（随机值）
        2.校验参数：（参数是否符合规则，判断是否有值）
        3.先从redis中取出内容真实的验证码内容
        4.与用户的验证码内容进行对比，如果对比不一致那么返回验证码输入错误
        5.如果一直，生成验证码的内容
        6.发送短信验证码
        7.告知发送结果
    '''
    # 1.获取参数：手机号码、图片验证码内容、图片验证码的编号（随机值）
    params_dict = request.json

    mobile = params_dict.get('mobile')
    image_code = params_dict.get('image_code')
    image_code_id = params_dict.get('image_code_id')

    # 2.校验参数：（参数是否符合规则，判断是否有值）
    # 判断参数是否正确
    if not all([mobile, image_code, image_code_id]):
        return jsonify(error=RET.PARAMERR, errmsg='参数错误')
    # 校验手机号是否正确
    if not re.match('1[35678]\\d{9}', mobile):
        return jsonify(error=RET.PARAMERR, errmsg='手机号格式不正确')

    # 3.先从redis中取出内容真实的验证码内容
    try:
        real_image_code = redis_store.get('ImageCodeId_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DATAERR, errmsg='数据查询失败')
    if not real_image_code:
        return jsonify(error=RET.NODATA, errmsg='图片验证码已过期')

    # 4.与用户的验证码内容进行对比，如果对比不一致那么返回验证码输入错误
    if real_image_code.upper() != image_code.upper():
        return jsonify(error=RET.DATAERR, errmsg='验证码输入错误')

    # 5.如果一直，生成验证码的内容
    # 随机数字，保证数字的长度为6位，不够再前面补上0
    sms_code_str = '%06d' % random.randint(0, 999999)
    current_app.logger.debug('短信验证码是： %s' % sms_code_str)
    # 6.发送短信验证码
    # result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES])
    # if result !=0:
    #     # 代表发送不成功
    #     return jsonify(error=RET.THIRDERR, errmsg='短信发送失败')
    # 保存验证码到redis
    try:
        redis_store.set('SMS_' + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='数据保存失败')
    # 7.告知发送结果
    return jsonify(error=RET.OK, errmsg='发送成功')

@passport_blu.route('/image_code')
def get_image_code():
    '''生成图片验证码并返回
        1.取到参数
        2.判断参数是否有值
        3.生成图片验证码
        4.保存图片验证码文字内容到redis
        5.返回图片验证码
    '''

    # 1.取到参数
    image_code_id = request.args.get('imageCodeId', None)
    # 2.判断参数是否有值
    if not image_code_id:
        return abort(403)
    # 3.生成图片验证码
    name, text, image = captcha.generate_captcha()
    current_app.logger.debug('图片验证码是 %s' % text)
    # 4.保存图片验证码文字内容到redis
    try:
        redis_store.set('ImageCodeId_' + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.debug(e)
        abort(500)
    # 5.返回图片验证码
    response = make_response(image)
    response.headers['Content_Type'] = 'image/jpg'
    return response
