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

