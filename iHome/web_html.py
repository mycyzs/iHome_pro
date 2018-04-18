# _*_ coding:utf-8 _*_
"""这里是获取静态文件"""
from flask import Blueprint
from flask import current_app

"""创建静态文件蓝图"""
html_blue = Blueprint('web_html',__name__)


"""需求，输入127.0.0.1：5000/register.html就可以访问静态文件
    同样当输入127.0.0.1：5000/时就访问的是主页
"""

@html_blue.route('/<re(r".*"):file_name>')
def get_static_html(file_name):

    """判断file_name有没有，没有就访问主页,当file_name没有值，是传不进来的，所以要自定义转换器，对参数过滤"""
    if not file_name:
        file_name = 'index.html'

    """主要拼接路径"""
    file_name = 'html/%s'%file_name

    """根据全路径，寻找文件并且响应给浏览器，开启上下文环境
        send_static_file 默认就会找到127.0.0.1：5000/static/ 所以拼接后面的就额可以类
    """
    return current_app.send_static_file(file_name)

