# _*_ coding:utf-8 _*_
"""这里是房屋相关的功能方法"""
from flask import current_app, jsonify
from flask import g
from flask import request

from iHome import constants
from iHome import db
from iHome.api_1_0 import api
from iHome.models import Area, House, Facility, HouseImage
from iHome.utils.common import check_login
from iHome.utils.response_code import RET
from iHome.utils.storage_images import upload_image


@api.route('/areas', methods=['GET'])
def get_areas():
    """查询所有的城区,得到的是对象"""
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.PARAMERR, errmsg='查找信息失败')

    # 构造字典列表
    area_list = []
    for area in areas:
        area_list.append(area.to_dict())

    return jsonify(reeno=RET.OK, errmsg='ok', data=area_list)


"""发布新房元时后台逻辑"""
@api.route('/houses', methods=['POST'])
@check_login
def pub_house():
    """
    是否登录
    1.接受参数，校验
    2.添加书库到数据库
    3.响应

    :return:
    """

    # 1,获取参数并校验
    json_dict = request.json
    title = json_dict.get('title')
    price = json_dict.get('price')
    address = json_dict.get('address')
    area_id = json_dict.get('area_id')
    room_count = json_dict.get('room_count')
    acreage = json_dict.get('acreage')
    unit = json_dict.get('unit')
    capacity = json_dict.get('capacity')
    beds = json_dict.get('beds')
    deposit = json_dict.get('deposit')
    min_days = json_dict.get('min_days')
    max_days = json_dict.get('max_days')
    facility = json_dict.get('facility')  # 一个列表[1,2]
    # 校验参数合法性
    if not all([title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days,
                facility]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    # 对于价格和押金是否合法，只可以传入数字
    # 数据库价格和押金字段限制的是整数，实际上价格押金也有带小数的，所以要把他乘以100变成整数，要取出来渲染的时候再除以100,关于金钱小数之类的都可以这样处理
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.PARAMERR, errmsg='金额格式错误')

    # 创建house对象，添加数据到表
    house = House()
    house.user_id = g.user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    # 给对象添加属性，模型类中relationship 只是添加关联方便查询，不会在表中创建字段
    facilities = Facility.query.filter(Facility.id.in_(facility)).all()
    house.facilities = facilities

    # 更新数据库信息
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(reeno=RET.DBERR, errmsg='添加数据失败')

    # 响应成功，带上房子的id，便于后面对于房屋的显示
    return jsonify(reeno=RET.OK, errmsg='发布成功', data={'house_id': house.id})


"""新房元发布成功后，隐藏原来的表单，上传房屋的表单就会显示出来，可以上传房子的图片"""
@api.route('/house/image', methods=['POST'])
@check_login
def upload_house_image():
    """
    用户是否登录
    获取参数并且校验
    查询房屋，只有房子存在时才上传
    调用七牛云工具上传
    把图片信息保存到house_image模型类中
    响应
    :return:
    """
    # 1.获取参数校验
    house_image = request.files.get('house_image')
    if not house_image:
        return jsonify(reeno=RET.PARAMERR, errmsg='获取图片失败')

    # 2.查询房屋信息,前端是form提交
    house_id = request.form.get('house_id')
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR, errmsg='查询出错')
    if not house:
        return jsonify(reeno=RET.NODATA, errmsg='房子不存在')

    # 3.调用工具上传
    try:
        key = upload_image(house_image)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.PARAMERR, errmsg='上传失败')

    # 创建House_image对象，添加属性
    image = HouseImage()
    image.house_id = house_id
    image.url = key

    # 给房子添加默认的图片
    if not house.index_image_url:
        house.index_image_url = key

    # 更新数据库
    try:
        db.session.add(image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(reeno=RET.DBERR, errmsg='图片保存失败')

    # 拼接图片的链接
    house_image_url = constants.QINIU_DOMIN_PREFIX + key

    return jsonify(reeno=RET.OK, errmsg='上传成功', data=house_image_url)


"""房子详情，拿到房子的id把相关信息显示，不用登录也可以查看"""
@api.route('/houses/<houseId>',methods=['GET'])
def house_detail(houseId):
    """获取房子id
        判断房子是否存在
        查询相关信息
        响应
    """
    # 1。获取房子并校验
    try:
        house = House.query.get(houseId)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR,errmsg='查询出错')
    if not house:
        return jsonify(reeno=RET.NODATA,errmsg='房子不存在')

    # 构造房子详情数据
    house_detail = house.to_full_dict()

    return jsonify(reeno=RET.OK,errmsg='ok',data = house_detail)