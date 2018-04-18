# _*_ coding:utf-8 _*_
"""项目公共的工具文件"""
from werkzeug.routing import BaseConverter

"""自定义转换器,用正则匹配外界的字符串"""

class RegConverter(BaseConverter):
    """调用父类的init方法"""
    def __init__(self,url_map,*args):
        super(RegConverter, self).__init__(url_map)

        self.regex = args[0]

