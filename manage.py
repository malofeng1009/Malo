from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    DEBUG = True

    # 为mysql添加配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/Information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)

# 加载配置
app.config.from_object(Config)

db = SQLAlchemy(app)
@app.route('/')
def index():

    return 'index'


if __name__ == '__main__':
    app.run(debug=True)
