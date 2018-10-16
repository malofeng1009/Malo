from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask import session
from info import db, create_app
# 通过指定的配置名创建对应配置的app
# create_app 就类似于工厂方法
app = create_app('development')


manager = Manager(app)
# 将 app 与 db 关联
Migrate(app, db)
# 将迁移命令添加到 manager 中
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    session['name'] = 'itheima'
    return 'index'


if __name__ == '__main__':
    manager.run()
