# _*_ coding:utf-8 _*_
"""这是订单模块"""
import datetime

from flask import current_app
from flask import g
from flask import request, jsonify

from iHome import db
from iHome.api_1_0 import api
from iHome.models import House, Order
from iHome.utils.common import check_login
from iHome.utils.response_code import RET

"""处理订单提交"""
@api.route('/orders',methods=['POST'])
@check_login
def sub_order():
    """创建、提交订单
    0.判断用户是否登录
    1.获取参数:house_id, start_date, end_date
    2.判断参数是否为空
    3.校验时间格式是否合法
    4.通过house_id，判断要提交的房屋是否存在
    5.判断当前房屋是否已经被预定了
    6.创建订单模型对象，并赋值
    7.将数据保存到数据库
    8.响应提交订单结果

    """
    # 获取参数
    json_dict = request.json
    house_id = json_dict.get('house_id')
    start_date_str = json_dict.get('start_date')
    end_date_str = json_dict.get('end_date')

    # 判断参数是否为空
    if not all([house_id,start_date_str,end_date_str]):
        return jsonify(reeno=RET.PARAMERR,errmsg='参数不合法')

    # 校验时间格式是否合法,看能不能转成时间格式
    try:
        start_date = datetime.datetime.strptime(start_date_str,'%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str,'%Y-%m-%d')
        if start_date and end_date:
            assert start_date < end_date,Exception('入住时间有误')

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.PARAMERR,errmsg='时间格式错误')

    # 判断房子是否粗在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='查询出错')
    if not house:
        return jsonify(reeno=RET.NODATA,errmsg='房子不存在')

    # 判断房子是否被预订类
    try:
        conflict_orders = Order.query.filter(Order.house_id==house_id,start_date<Order.end_date,end_date>Order.begin_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='查询出错')
    if conflict_orders:
        return jsonify(reeno=RET.PARAMERR,errmsg='该房屋已经被预订类')

    # 创建订单模型对象，赋值

    order = Order()
    order.user_id = g.user_id
    order.house_id = house_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = (end_date - start_date).days  # days是datetime模块中的属性
    order.house_price = house.price
    order.amount = order.days * house.price

    # 将数据把存到数据库
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(reeno=RET.DBERR,errmsg='查询出错')

    return jsonify(reeno=RET.OK,errmsg='ok')



"""显示我的订单页面"""
@api.route('/orders')
@check_login
def get_orders():
    """
    0.判断用户是否登录
    1.获取当前登录用户的user_id
    2.使用user_id查询用户的所有的订单信息
    3.构造响应数据
    4.响应数据

    """
    # 获取当前用户id
    # 获取参数role，role=custom是租客,role=landlord是房东
    role = request.args.get('role')
    # 判断role
    if role not in ['custom','landlord']:
        return jsonify(reeno=RET.PARAMERR,errmsg='参数有误')

    user_id = g.user_id

    # 查询所有的订单
    try:
        if role == 'custom':
            orders = Order.query.filter(Order.user_id == user_id).all()
        else:
            houses = House.query.filter(House.user_id == user_id).all()  #获取房东所有的房屋
            houses_ids = [house.id for house in houses]
            orders = Order.query.filter(Order.house_id.in_(houses_ids)).all()


    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='查询失败')
    if not orders:
        return jsonify(reeno=RET.NODATA,errmsg='没有订单')

    # 构造响应参数
    response_dict = []
    for order in orders:
        response_dict.append(order.to_dict())

    return jsonify(reeno=RET.OK,errmsg='ok',data = response_dict)


"""房东接单，改变订单的状态"""
@api.route('/orders/<order_id>',methods=['POST'])
@check_login
def accept_order(order_id):
    """
      0.判断用户是否登录
    1.根据order_id查询订单信息,需要指定订单状态为"待接单"
    2.判断当前登录是否是否是该订单中的房屋的房东
    3.修改订单状态为"已接单"
    4.保存到数据库
    5.响应结果

    """
    # 获取参数action，区分是接单还是拒单的请求

    action = request.args.get('action')
    if action not in ['accept','reject']:
        return jsonify(reeno=RET.PARAMERR,errmsg='参数错误')

    # 查询
    try:

        order = Order.query.filter(Order.id == order_id,Order.status == 'WAIT_ACCEPT').first()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='查询出错')
    if not order:
        return jsonify(reeno=RET.NODATA,errmsg='订单不粗在')

    # 判断是否是房东
    order_user_id = order.house.user_id
    user_id = g.user_id
    if order_user_id != user_id:
        return jsonify(reeno=RET.PARAMERR,errmsg='用户身份信息错误')

    # 修改订单状态
    if action == 'accept':
        order.status = 'WAIT_COMMENT'
    else:
        order.status = 'REJECTED'
        reason = request.json.get('reason')
        if reason:
            order.comment = reason

    # 包粗到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='保存失败')

    return jsonify(reeno=RET.OK,errmsg='ok')


"""用户评价"""
@api.route('/orders/comment/<order_id>',methods=['POST'])
@check_login
def order_comment(order_id):
    """
    0.判断用户是否登录
    1.接受参数：order_id，comment,并校验
    2.使用order_id查询"待评价"的订单数据
    3.修改订单状态为"已完成"。并保存评价信息
    4.保存数据到数据库
    5.响应评价结果

    """
    # 获取参数
    comment = request.json.get('comment')
    if not comment:
        return jsonify(reeno=RET.PARAMERR,errmsg='缺少必传参数')

    # 根据order_id，查询订单信息
    try:
        order = Order.query.filter(Order.id == order_id,Order.status == 'WAIT_COMMENT',Order.user_id == g.user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='查询出错')
    if not order:
        return jsonify(reeno=RET.NODATA,errmsg='订单不存在')

    # 修改订单状态/
    order.status = 'COMPLETE'
    order.comment = comment

    # 更新数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(reeno=RET.DBERR,errmsg='保存数据出错')

    return jsonify(reeno=RET.OK,errmsg='ok')