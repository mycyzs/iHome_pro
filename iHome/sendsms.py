#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

#���ʺ�
accountSid= '8a216da862dcd1050162dd2df48f006f'

#���ʺ�Token
accountToken= '87509addc73847bab7c875cb0613dd71'

#Ӧ��Id
appId='8a216da862dcd1050162dd2df4f30075'

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

#����˿� 
serverPort='8883'

#REST�汾��
softVersion='2013-12-26'

  # ����ģ�����
  # @param to �ֻ�����
  # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
  # @param $tempId ģ��Id

"""����һ���࣬�����з����ŵķ���"""
class ScpS(object):
    """Ϊ�˲�����ÿ�δ����Ը���������ʹ��һ������"""
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
        for k, v in result.iteritems():

            if k == 'templateSMS':
                for k, s in v.iteritems():
                    print '%s:%s' % (k, s)
            else:
                print '%s:%s' % (k, v)



# ����ģ�����
# @param to �ֻ�����
# @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
# @param $tempId ģ��Id

# def sendTemplateSMS(to,datas,tempId):
#
#
#     #��ʼ��REST SDK
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
    
   
# sendTemplateSMS('15920407822',['666666',5],1)