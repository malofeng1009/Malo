from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from info import create_app, models, db

# manager.py 是程序的启动入口，只关心启动的相关参数以及内容，不关心具体
# 只创建 app 或者相关业务逻辑

# 通过指定的配置名创建对应配置的app
# create_app 就类似于工厂方法
from info.models import User

app = create_app('development')

manager = Manager(app)
# 将 app 与 db 关联
Migrate(app, db)
# 将迁移命令添加到 manager 中
manager.add_command('db', MigrateCommand)


@manager.option('-n', '-name', dest="name")
@manager.option('-p', '-password', dest="password")
def createsuperuser(name, password):

    if not all([name, password]):
        print("参数不足")

    user = User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)

    print("添加成功")
if __name__ == '__main__':
    manager.run()
