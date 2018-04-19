# _*_ coding:utf-8 _*_
"""生成验证码和发送短信功能"""
import logging
from flask import abort, jsonify
from flask import current_app
from flask import make_response
from flask import request

from iHome import constants
from iHome import redis_strict
from iHome.utils.captcha.captcha import captcha
from iHome.api_1_0 import api
from iHome.utils.response_code import RET

"""生成新的验证码就应该把上次的uuid删除掉"""
last_uuid = ""

"""定义获取验证码的方法,访问127.0.0.1：5000/api/1.0/image_code"""
@api.route('/image_code',methods=['GET'])
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
    name,text,image = captcha.generate_captcha()
    """打印日志记录错误信息"""
    # logging.debug(text)
    current_app.logger.debug(text)
    """使用redis存储验证码的值，uuid作为key，设置过期时间，常量不应该写在代码"""
    try:
        if last_uuid:
            redis_strict.delete('ImageCode:%s'%last_uuid)

        redis_strict.set('ImageCode:%s'%uuid,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        """打印日志保存错误信息"""
        # logging.error(e)
        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR,errmsg='保存验证码失败')

    """声明全局变量,保存目前的uuid"""
    global last_uuid
    last_uuid = uuid

    """响应验证码图片给浏览器显示"""
    response = make_response(image)
    """修改响应头的文件类型，浏览器默认是text/html，改成image/jpg才可以正常显示图片"""
    response.headers['Content-Type'] = 'image/jpg'
    return response
