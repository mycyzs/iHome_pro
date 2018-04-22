# _*_ coding:utf-8 _*_
"""项目公共的工具文件"""
from functools import wraps

from flask import g
from flask import session, jsonify
from werkzeug.routing import BaseConverter

from iHome.utils.response_code import RET

"""自定义转换器,用正则匹配外界的字符串"""

class RegConverter(BaseConverter):
    """调用父类的init方法"""
    def __init__(self,url_map,*args):
        super(RegConverter, self).__init__(url_map)

        self.regex = args[0]




"""定义一个装饰器用于登录检测，要判断是否登录只要把函数装饰一下即刻"""
# 把函数当成参数传入
def check_login(func):
    """自定义装饰器判断用户是否登录
        使用装饰器装饰函数时，会修改被装饰的函数的__name属性和被装饰的函数的说明文档
        为了不让装饰器影响被装饰的函数的默认的数据，我们会使用@wraps装饰器，提前对view_funcJ进行装饰
        """
    @wraps(func)
    def set_func(*args,**kwargs):
        """在这里判断一下用户是否登录，装饰器就是在不改变原来函数的调用以及结果添加一些额外的功能"""
        user_id = session.get('user_id')

        if not user_id:
            return jsonify(reeno=RET.NODATA,errmsg='用户未登录')

        else:
            """用g变量记录用户的id，方便调用装饰器的视图函数使用"""
            g.user_id = user_id
            """执行被装饰的视图函数"""
            return func(*args,**kwargs)

    return set_func



