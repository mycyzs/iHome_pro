# _*_ coding:utf-8 _*_
"""这里是房屋相关的功能方法"""
import datetime
from flask import current_app, jsonify
from flask import g
from flask import request
from flask import session

from iHome import constants, redis_strict
from iHome import db
from iHome.api_1_0 import api
from iHome.models import Area, House, Facility, HouseImage, Order
from iHome.utils.common import check_login
from iHome.utils.response_code import RET
from iHome.utils.storage_images import upload_image


@api.route('/areas', methods=['GET'])
def get_areas():
    """查询所有的城区,得到的是对象
    """
    """
        既然有缓存就首先尝试获取redis中的缓存，提高效率，减轻网站的压力
    """
    try:
        area_list = redis_strict.get('Areas')
        if area_list:
            return jsonify(reeno=RET.OK,errmsg='ok')
    except Exception as e:
        current_app.logger.error(e)

    # 直接查询所有的城区
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.PARAMERR, errmsg='查找信息失败')

    # 构造字典列表
    area_list = []
    for area in areas:
        area_list.append(area.to_dict())

    # 把数据缓存起来，因为后面也有用到区域信息，把缓存放到redis数据库
    # 就算缓存失败也不要return，因为会阻碍后面代码的执行
    try:
        redis_strict.set('Areas',area_list,constants.AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)




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

    # 尝试获取用户id，有可能不存在
    login_user_id = session.get('user_id',-1)


    return jsonify(reeno=RET.OK,errmsg='ok',data = house_detail,login_user_id = login_user_id)


"""显示首页最新的五个房屋，轮播"""
@api.route('/houses/index')
def swiper_index():
    """
        查询最新的五个房屋
        查询出来的是对象，转成字典列表

    :return:
    """
    # 查询最新5个房子
    try:
        houses = House.query.order_by(House.create_time.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.PARAMERR,errmsg='查询出错')

    # 转成字典列表
    house_dict = []
    for house in houses:
        house_dict.append(house.to_basic_dict())

    return jsonify(reeno=RET.OK,errmsg='ok',data = house_dict)


"""用户点击搜索之后显示的界面"""
@api.route('/houses/search')
def search_house():

    """
    接受参数，显示该区域所有的房屋
    :return:
    """
    # 1.接受参数
    aid = request.args.get('aid')
    # 获取排序规则；new:根据发布时间倒叙；booking：根据订单量倒叙；price-inc:根据价格由低到高；price-des：根据价格由高到低
    sk = request.args.get('sk','')
    # 打印一下
    current_app.logger.debug(sk)
    # 获取当前要显示的页码
    p = request.args.get('p')
    # 获取用户入住和离开的时间
    sd = request.args.get('sd')
    ed = request.args.get('ed')
    start_date=None
    end_date = None
    # 对页数进行验证
    try:
        p = int(p)
        # 验证用户的入住和离开时间
        if sd:      #把字符串转成时间格式
            start_date = datetime.datetime.strptime(sd,'%Y-%m-%d')
        if ed:
            end_date = datetime.datetime.strptime(ed,'%Y-%m-%d')
        if start_date and end_date:         #如果这两个都有，就断言
            assert start_date < end_date,Exception('入住时间有误') #主动抛出异常，让后面的代码可以捕获到

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.PARAMERR,errmsg='参数错误')


    try:
        # 得到basequery对象
        house_query = House.query
        # 用户有没有选择区域都可以
        if aid:
            house_query = house_query.filter(House.area_id == aid)

        conflict_orders = []
        # 根据用户选中的入住和离开时间，筛选出对应的房屋信息（需要将已经在订单中的时间冲突的房屋过滤掉）
        if start_date and end_date:
            conflict_orders = Order.query.filter(start_date<Order.end_date,end_date>Order.begin_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(start_date<Order.end_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(end_date>Order.begin_date).all()

        # 查询出这部分冲突订单中的房子,先有数据再进行分页或者是排序，大到小
        if conflict_orders:
            house_ids = [order.house_id for order in conflict_orders]
        # 查询出不包含这些house_id的房屋
            house_query = house_query.filter(House.id.notin_(house_ids))
        # 根据用户选择排序房屋
        if sk == 'booking':  # 根据订单量倒叙
            house_query = house_query.order_by(House.order_count.desc())
        elif sk == 'price-inc':  # 根据价格由低到高
            house_query = house_query.order_by(House.price.asc())
        elif sk == 'price-des':  # 根据价格由高到低
            house_query = house_query.order_by(House.price.desc())
        else:  # 默认就是new,根据发布时间倒叙
            house_query = house_query.order_by(House.create_time.desc())

        # 获取所有的房屋
        # houses = house_query.all()
        # 使用分页查询指定条数的数据:参数1，是要读取的页码，参数2，是每页数据条数，参数3，默认有错不输出
        # 一般分页会放在把数据查询出来之后
        paginate = house_query.paginate(p,constants.HOUSE_LIST_PAGE_CAPACITY,False)
        # 获取当前页的模型对象
        houses = paginate.items
        # 获取总的页数
        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.PARAMERR,errmsg='查找房屋失败')

    # 转成字典列表
    house_list = []

    for house in houses:
        house_list.append(house.to_basic_dict())

    # 从新构造参数，字典加多一层
    respinse_dict = {
        'house':house_list,
        'total_page':total_page
    }

    return jsonify(reeno=RET.OK,errmsg='ok',data = respinse_dict)