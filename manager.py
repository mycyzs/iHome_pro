# _*_ coding:utf-8 _*_
"""程序入口"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis


class Config(object):
    """配置参数"""
    DEBUG = True
    """配置mysql数据库，真是开发不写127"""
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome_pro'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """配置redis数据库，开发用真实的"""
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379


app = Flask(__name__)

"""加载配置参数"""
app.config.from_object(Config)

"""创建链接到数据库的对象"""
db = SQLAlchemy(app)

"""创建链接redis的对象"""
redis_strict = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)



@app.route('/')
def index():
    """测试redis是否链接"""
    # redis_strict.set('name','python')
    return 'index'

if __name__ == '__main__':
    app.run()