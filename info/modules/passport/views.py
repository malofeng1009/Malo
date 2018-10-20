import random
import re
from flask import request, abort, current_app, make_response, jsonify
from info import redis_store, constants
from info.libs.yuntongxun.sms import CCP
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import  passport_blu


@passport_blu.roule('/sms_code', methods=['post'])
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
    result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES])
    if result !=0:
        # 代表发送不成功
        return jsonify(error=RET.THIRDERR, errmsg='短信发送失败')
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
