# _*_ coding:utf-8 _*_
"""模拟首页，项目中没用到"""
from . import api
from iHome import redis_strict

@api.route('/')
def index():
    """测试redis是否链接"""
    redis_strict.set('name','python')
    """测试session过期时间"""
    # session['celery'] = 1000
    return 'index'