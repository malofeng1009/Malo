from flask import Blueprint, session, request, redirect, url_for

# 创建蓝图对象
admin_blu = Blueprint('admin', __name__, url_prefix='/admin')

from . import views


@admin_blu.before_request
def check_admin():
    # print("admin before_request")
    # if 不是管理员，那么直接跳转到主页
    is_admin = session.get("is_admin", False)
    # if not is_admin and 当前访问的url不是管理登录页:
    if not is_admin and not request.url.endswith(url_for('admin.login')):
        return redirect('/')