# _*_ coding:utf-8 _*_

"""按照蓝图划分模块"""
from flask import Blueprint

"""创建版本1.0的蓝图,路径开头带上版本号"""
api = Blueprint('api_1_0',__name__,url_prefix='/api/1.0')

"""执行这个文件的时候导入并且执行"""
from iHome.api_1_0 import index,verify,passport,userinfo
"""执行创建验证码的文件"""
