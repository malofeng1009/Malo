from flask import request, abort, current_app, make_response
from info import redis_store, constants
from info.utils.captcha.captcha import captcha
from . import  passport_blu


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
