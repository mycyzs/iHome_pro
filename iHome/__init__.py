# coding=utf-8

"""得到app和db文件"""
"""创建应用模块"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from config import Config,configs
from flask_session import Session
from iHome.utils.common import RegConverter

"""创建链接到mysql数据库的对象"""
db = SQLAlchemy()
"""定义全局对象redis_strict"""
redis_strict = None


"""定义一个方法获取不同模式下配置得到的app"""
def get_app(class_name):



    app = Flask(__name__)

    """加载配置参数"""
    # app.config.from_object(Config)
    app.config.from_object(configs[class_name])

    """创建链接到数据库的对象"""
    # db = SQLAlchemy(app)
    db.init_app(app)
    """创建链接redis的对象"""
    global redis_strict #声明全局变量
    redis_strict = redis.StrictRedis(host=configs[class_name].REDIS_HOST,port=configs[class_name].REDIS_PORT)

    """开启csrf保护，防止跨站伪造请求，post，path，put，delete方法会开启，flask中要自己将csrf_token写入浏览器的cookie
        csrf_token写入session，所以要secret_key
    """
    CSRFProtect(app)

    """将自定义转换器添加到app"""
    app.url_map.converters['re'] = RegConverter

    """哪里用到蓝图注册，哪里导入"""
    from iHome.api_1_0 import api
    app.register_blueprint(api)

    """注册蓝图，获取静态文件"""
    from iHome.web_html import html_blue
    app.register_blueprint(html_blue)

    """将session数据写入redis数据库"""
    Session(app)

    return app