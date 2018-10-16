from info import redis_store
from . import index_blu


@index_blu.route('/')
def index():
    # session['name'] = 'itheima'

    # 测试打印日志

    # current_app.logger.debug('测试debug')
    # current_app.logger.error('测试error')
    # current_app.logger.fatal('测试fatal')

    # 向 redis 中保存一个字 name itcast
    redis_store.set('name', 'itcast')
    return 'index'
