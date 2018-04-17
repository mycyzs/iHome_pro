# _*_ coding:utf-8 _*_
"""程序入口"""
from flask import Flask


class Config(object):
    """配置参数"""
    DEBUG = True

app = Flask(__name__)


"""加载配置参数"""
app.config.from_object(Config)

@app.route('/')
def index():
    pass

if __name__ == '__main__':
    app.run()