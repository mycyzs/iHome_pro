# _*_ coding:utf-8 _*_
"""生成验证码和发送短信功能"""
import logging
import random
import re

from flask import abort, jsonify
from flask import current_app
from flask import json
from flask import make_response
from flask import request

from iHome import constants
from iHome import redis_strict
from iHome.models import User
from iHome.sendsms import ScpS
from iHome.utils.captcha.captcha import captcha
from iHome.api_1_0 import api
from iHome.utils.response_code import RET

"""定义发送短信的方法"""


@api.route('/sms_code', methods=['POST'])
def send_sms():
    """当验证码图片刷新并且保存了值到数据库，用户此时输入手机号，验证码，当用户点击验证码的时候，发起ajax的post请求"""
    """发送短信验证码
       1.获取参数:手机号，验证码，uuid
       2.判断是否缺少参数，并对手机号格式进行校验
       3.获取服务器存储的验证码
       4.跟客户端传入的验证码进行对比
       5.如果对比成功就生成短信验证码
       6.调用单例类发送短信
       7.如果发送短信成功，就保存短信验证码到redis数据库
       8.响应发送短信的结果
       """
    # 1.获取参数:手机号，验证码，uuid
    json_str = request.data
    json_dict = json.loads(json_str)
    mobile = json_dict.get('mobile')
    ImageCode = json_dict.get('ImageCode')
    uuid = json_dict.get('uuid')
    current_app.logger.debug(uuid)

    # 发送短信的时候，如果该手机号已经注册就不再发送短信类
    # 手机号码已经注册就不可以再次注册了
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR, errmsg='查询数据库出错')
    if user:
        return jsonify(reeno=RET.DATAEXIST, errmsg='用户已存在')

    # 2.判断是否缺少参数，并对手机号格式进行校验
    if not all([mobile, ImageCode, uuid]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不能为空')
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(reeno=RET.NODATA, errmsg='手机号不恩改为空')

    # 3.获取服务器存储的验证码
    try:
        image_code_server = redis_strict.get('ImageCode:%s' % uuid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR, errmsg='查询验证码失败')
    if not image_code_server:
        return jsonify(reeno=RET.NODATA, errmsg='验证码不存在')

    # 跟客户端传入的验证码进行对比
    if ImageCode.lower() != image_code_server.lower():
        return jsonify(reeno=RET.PARAMERR, errmsg='验证码输入错误！！')

    # 手动生成短信验证码,在0-999999范围内生成一个六位数的随机数，不足用0补齐
    sms_code = '%06d' % random.randint(0, 999999)
    # 日志记录仪下
    current_app.logger.debug(sms_code)

    # 调用单例类发送短信

    result = ScpS().sendTemplateSMS(mobile, [sms_code, 5], 1)
    if result != 1:
        return jsonify(reeno=RET.PARAMERR, errmsg='发送短信失败')

    # 保存自己生成的验证码到redis，方便后面注册时做验证,设置过期时间
    print (type(mobile), type(sms_code))
    try:
        """unicode string和byte string 不可以混用"""
        redis_strict.set('SMS：%s' % mobile.encode('utf-8'), sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(reeno=RET.DBERR, errmsg='验证码保存失败')

    # 响应成功
    return jsonify(reeno=RET.OK, errmsg='发送验证码成功')


"""生成新的验证码就应该把上次的uuid删除掉"""
last_uuid = ""

"""定义获取验证码的方法,访问127.0.0.1：5000/api/1.0/image_code"""
"""此方法主要生成图片验证码和保存验证码的值在redis中"""


@api.route('/image_code', methods=['GET'])
def get_image_code():
    """需要注意的是，当页面生成类图片验证码，就应该把验证码的值存入redis数据库
        此时需要一个唯一识别码 uuid 作为key，保存在redis数据库，加载页面的时候
        加载js给验证码图片注入url，带上uuid，马上把验证码的值存入redis数据库，
        当用户填写了验证码，再跟数据库的验证码对比，通过则进行下一步发送短信
    """
    """验证码图片src='/api/1.0/image_code?uuid=hdahdakk'"""
    uuid = request.args.get('uuid')
    """判断uuid是否有值"""
    print uuid
    if not uuid:
        abort(403)

    """利用第三方框架生成图片验证码，返回值"""
    name, text, image = captcha.generate_captcha()
    """打印日志记录错误信息"""
    # logging.debug(text)
    current_app.logger.debug(text)
    """使用redis存储验证码的值，uuid作为key，设置过期时间，常量不应该写在代码"""
    try:
        if last_uuid:
            redis_strict.delete('ImageCode:%s' % last_uuid)

        redis_strict.set('ImageCode:%s' % uuid, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        """打印日志保存错误信息"""
        # logging.error(e)
        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR, errmsg='保存验证码失败')

    """声明全局变量,保存目前的uuid"""
    global last_uuid
    last_uuid = uuid

    """响应验证码图片给浏览器显示"""
    response = make_response(image)
    """修改响应头的文件类型，浏览器默认是text/html，改成image/jpg才可以正常显示图片"""
    response.headers['Content-Type'] = 'image/jpg'
    return response
