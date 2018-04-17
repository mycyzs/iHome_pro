#coding=utf-8
"""这里是配置文件"""
import redis



class Config(object):
    """配置参数"""
    DEBUG = True
    """配置密钥，session要配置密钥"""
    SECRET_KEY = 'q7pBNcWPgmF6BqB6b5VICF7z7pI+90o0O4CaJsFGjzRsYiya9SEgUDytXvzFsIaR'
    """配置mysql数据库，真是开发不写127"""
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome_pro'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """配置redis数据库，开发用真实的"""
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    """配置session参数"""
    """指定session存储到redis数据库"""
    SESSION_TYPE = 'redis'
    """指定redis的位置"""
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    """是否使用secret_key签名session_data"""
    SESSION_USE_SIGNER = True
    """设置session过期时间,默认一个月"""
    PERMANENT_SESSION_LIFETIME = 3600 * 24  # 有效期为一天



"""用工厂模式针对不同阶段项目的配置不同，主要是把配置参数赋值给flask对象app，不同模式下的类继承
    Config，不同阶段稍作修改即可
"""

class Development(Config):
    """开发模式下的配置"""
    pass


class Production(Config):
    """生产环境、线上、部署之后"""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome_GZ'
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 2  # 有效期为一天


class UnitTest(Config):
    """测试环境"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome_GZ01_unittest'

# 准备工厂要使用的原材料
configs = {
    'dev': Development,
    'pro': Production,
    'test': UnitTest
}