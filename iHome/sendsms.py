#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

#主帐号
accountSid= '8a216da862dcd1050162dd2df48f006f'

#主帐号Token
accountToken= '87509addc73847bab7c875cb0613dd71'

#应用Id
appId='8a216da862dcd1050162dd2df4f30075'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id

"""创建一个类，对象有发短信的方法"""
class ScpS(object):
    """为了不让其每次创建对各对象，所以使用一个单例"""
    _isinstance = None
    def __new__(cls, *args, **kwargs):
        if cls._isinstance == None:
            cls._isinstance = super(ScpS, cls).__new__(cls,*args,**kwargs)
            cls._isinstance.rest = REST(serverIP, serverPort, softVersion)
            cls._isinstance.rest.setAccount(accountSid, accountToken)
            cls._isinstance.rest.setAppId(appId)
        return cls._isinstance

    def sendTemplateSMS(self,to,datas,tempId):


        result = self.rest.sendTemplateSMS(to, datas, tempId)
        print result.get('statusCode')

        """判断发送 成功与否"""
        if result.get('statusCode') == '000000':
            return 1
        else:
            return 0
#

        # smsMessageSid:03
        # d77fbe6831497db29db2efa2b67091
        # dateCreated:20180419202305
        # statusCode:000000
# ScpS().sendTemplateSMS('15920407822',['666666',5],1)


# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id

# def sendTemplateSMS(to,datas,tempId):
#
#
#     #初始化REST SDK
#     rest = REST(serverIP,serverPort,softVersion)
#     rest.setAccount(accountSid,accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to,datas,tempId)
#     for k,v in result.iteritems():
#
#         if k=='templateSMS' :
#                 for k,s in v.iteritems():
#                     print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)
#
#
# sendTemplateSMS('15920407822',['666666',5],1)