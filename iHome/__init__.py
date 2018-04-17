# coding=utf-8

"""得到app和db文件"""
"""创建应用模块"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from config import Config




app = Flask(__name__)

"""加载配置参数"""
app.config.from_object(Config)

"""创建链接到数据库的对象"""
db = SQLAlchemy(app)

"""创建链接redis的对象"""
redis_strict = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

"""开启csrf保护，防止跨站伪造请求，post，path，put，delete方法会开启，flask中要自己将csrf_token写入浏览器的cookie"""
CSRFProtect(app)