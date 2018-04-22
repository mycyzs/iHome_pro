# _*_ coding:utf-8 _*_
"""这里处理用户相关的功能"""
from flask import current_app
from flask import g
from flask import request, jsonify
from flask import session

from iHome import constants, db
from iHome.api_1_0 import api
from iHome.models import User
from iHome.utils.common import check_login
from iHome.utils.response_code import RET
from iHome.utils.storage_images import upload_image

"""显示个人头像"""
@api.route('/users/avatar',methods=['POST'])
@check_login            #调用装饰器检测用户是否登录
def upload_avatar():
    """这里是用户修改个人信息的界面"""
    """
    需要检验是否登录
    1.获取用户上传的头像数据，并校验
    2.查询当前的登录用户
    3.调用上传工具方法实现用户头像的上传
    4.将用户头像赋值给当前的登录用户的user模型
    5.将数据保存到数据库
    6.响应上传用户头像的结果
    """
    # 1.获取上传的头像数据，校验
    image_data = request.files.get('avatar')
    if not image_data:
        return jsonify(reeno=RET.PARAMERR,errmsg='图片获取失败')

    # 2.查询当前的用户
    # user_id = session.get('user_id')
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.PARAMERR,errmsg='查询数据库失败')
    if not user:
        return jsonify(reeno=RET.NODATA,errmsg='用户不存在')

    # 3.调用上传方法上传图片到七牛云,得到数据的标识key
    try:
        key = upload_image(image_data)
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(reeno=RET.PARAMERR,errmsg='上传图片失败')

    # 4.添加对象属性
    user.avatar_url = key

    # 5.更新用户数据库信息
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='图片保存失败')


    # 响应结果
    avatar_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(reeno=RET.OK,errmsg='上传图片成功',data=avatar_url)

"""修改名字，用PUT提交"""
@api.route('/users/names',methods=['PUT'])
@check_login
def update_name():
    """
    需要检验是否登录
    1.获取新的用户名，并判断是否为空
    2.查询当前的登录用户
    3.将新的用户名赋值给当前的登录用户的user模型
    4.将数据保存到数据库
    5.响应修改用户名的结果
    :return:
    """
    # 获取用户名
    new_name = request.json.get('name')
    if not new_name:
        return jsonify(reeno=RET.PARAMERR,errmsg='不嫩为空空')

    # 查询当前登录的用户
    # user_id = session['user_id']
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='查询数据库错误')

    # 赋值
    user.name = new_name

    # 更新用户数据库的信息
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(reeno=RET.DBERR,errmsg='保存信息出错')

    return jsonify(reeno=RET.OK,errmsg='修改信息成功')


"""查询用户信息,在修改中心显示"""
@api.route('/users',methods=['GET'])
@check_login
def show_user_info():
    """
    # 需要检验是否登录
    1.从session中获取当前登录用户的user_id
    2.查询当前登录用户的user信息
    3.构造个人信息的响应数据
    4.响应个人信息的结果
    :return:
    """
    # 1.获取当前登录的用户
    # user_id = session['user_id']
    user_id = g.user_id     #检验到用户已登录就已经用g保存着用户的user_id了
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.PARAMERR,errmsg='查询数据库错误')
    if not user:
        return jsonify(reeno=RET.PARAMERR,errmsg='用户不存在')

    # 用户信息
    response_user_info = user.to_dict()

    return jsonify(reeno=RET.OK,errmsg='ok',data = response_user_info)


"""用户实名认证"""
@api.route('/users/auth',methods=['POST'])
@check_login
def set_real_name():
    """
    也需要判断用户是否登录
    1.获取参数，校验参数
    2.确认当前登录用户
    3.给用户赋值
    4.更新用户数据库信息
    5.响应
    :return:
    """
    # 1.获取参数，检验
    json_dict = request.json
    real_name = json_dict.get('real_name')
    id_card = json_dict.get('id_card')

    if not all([real_name,id_card]):
        return jsonify(reeno=RET.PARAMERR,errmsg='参数不正确')

    # 2当前登录用户
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='查找用户出错')
    if not user:
        return jsonify(reeno=RET.NODATA,errmsg='用户不存在')

    # 3.给用户属性添加值
    user.real_name = real_name
    user.id_card = id_card

    # 4.更新用户信息
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(reeno=RET.DBERR,errmsg='保存信息出错')

    return jsonify(reeno=RET.OK,errmsg='实名认证通过')

@api.route('/users/info',methods=['GET'])
@check_login
def real_name_info():
    """查询用户的实名认证数据
        1.判断用户登录
        2.获取用户信息
        3.响应前端
    """
    # 确认当前用户
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='查找出错')
    if not user:
        return jsonify(reeno=RET.NODATA,errmsg='用户不存在')

    # 获取用户信息
    user_info = user.real_name_data()

    return jsonify(reeno=RET.OK,errmsg='ok',data = user_info)