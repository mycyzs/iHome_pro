# _*_ coding:utf-8 _*_
"""这里实现注册功能"""
import re

from flask import Flask, jsonify
from flask import current_app
from flask import g
from flask import json
from flask import request
from flask import session

from iHome import redis_strict, db
from iHome.utils.common import check_login
from . import api
from iHome.models import User
from iHome.utils.response_code import RET


"""处理退出"""
@api.route('/sessions',methods=['DELETE'])
def logout():
    """退出即把session数据删除，没有保持的公路状态"""
    session.pop('user_id')
    session.pop('mobile')
    session.pop('name')

    return jsonify(reeno=RET.OK,errmsg='退出成功')

@api.route('/sessions',methods=['POST'])
def login():
    """处理登录逻辑"""
    """
    1.获取用户输入的信息
    2.验证参数的合法性
    3.校验用户的信息是否正确
    4.查询数据库是否有这个用户
    4.session保持用户登录状态
    5.响应数据
    """
    # 1.获取用户输入的信息
    json_dict = request.json
    mobile = json_dict.get('mobile')
    password = json_dict.get('password')

    # 2.验证参数合法性
    if not all([mobile,password]):
        return jsonify(reeno=RET.PARAMERR,errmsg='参数不能为空')
    if not re.match(r'^1[345678][0-9]{9}$',mobile):
        return jsonify(reeno=RET.PARAMERR,errmsg='手机格式不正确')

    # 查询数据库用户是否存在
    try:
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='查询数据库出错')
    if not user:
        return jsonify(reeno=RET.NODATA,errmsg='用户或者密码错误')

    # 校验密码是否输入有错，flask提供的密码检验方法，跟传进来的比较就行
    if not user.check_password(password):
        return jsonify(reeno=RET.NODATA,errmsg='密码或者用户名错误')

    # session保持用户登录状态
    session["user_id"] = user.id
    session['name'] = user.name
    session['mobile'] = user.mobile

    return jsonify(reeno=RET.OK,errmsg='登录成功')




@api.route('/users',methods=['POST'])
def register():
    """注册
       1.获取注册参数：手机号，短信验证码，密码
       2.判断参数是否缺少
       3.获取服务器存储的短信验证码
       4.与客户端传入的短信验证码对比
       5.如果对比成功，就创建用户模型User对象，并给属性赋值
       6.将模型属性写入到数据库
       7.响应注册结果
       """
    # 获取注册参数：手机号，短信验证码，密码
    # 拿到所有的数据，三种方法
    # json_str = request.data
    # json_dict = json.loads(json_str)
    # 如果肯定传过来的是json数据，可以用以下两种简便的方法
    # json_dict = request.get_json()
    json_dict = request.json
    mobile = json_dict.get('mobile')
    sms_code = json_dict.get('sms_code')
    password = json_dict.get('password')

    # 判断参数是否缺少
    if not all([mobile,sms_code,password]):
        return jsonify(reeno=RET.PARAMERR,errmsg='缺少参数')
    # 判断手机号是否符合格式
    if not re.match(r'^1[345678][0-9]{9}$',mobile):
        return jsonify(reeno=RET.PARAMERR,errmsg='手机还格式错误')
    # 获取服务器短信验证码，有可能过期类获取不到
    try:
        sms_code_server = redis_strict.get('SMS：%s'%mobile.encode('utf-8'))
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='获取服务器验证码错误')



    # 对比用户输入的验证码，通过的话就进行注册功能
    if sms_code != sms_code_server:
        return jsonify(reeno=RET.PARAMERR,errmsg='短信验证码输入有误！！')

    # 把用户信息保存到数据库，完成注册流程
    user = User()
    user.mobile = mobile
    # 需要将密码加密后保存到数据库:调用password属性的setter方法,这里只是赋一个属性，并不是表中的字段
    user.password = password
    user.name = mobile

    # 将对象保存到数据库
    try:

        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        """回滚操作"""
        db.session.rollback()
        return jsonify(reeno=RET.DBERR,errmsg='保存信息错误')

    """注册即登录，生成注册时数据的保持状态"""
    session['user_id'] = user.id
    session['name'] = user.name
    session['mobile'] = user.mobile

    # 注册成功，响应
    return jsonify(reeno=RET.OK,errmsg='注册成功')


#
"""以登录的用户首页显示用户名"""
@api.route('/sessions',methods=['GET'])
def check_logins():
    """判断用户是否登录
    从session中获取数据
    """
    """获取数据"""

    name = session.get('name')
    if not name:
        return jsonify(reeno=RET.PARAMERR,errmsg='用户未登录')

    return jsonify(reeno=RET.OK,errmsg='ok',data = {'name':name})