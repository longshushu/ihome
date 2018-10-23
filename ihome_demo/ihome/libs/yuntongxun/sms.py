# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from CCPRestSDK import REST
import ConfigParser

# 主帐号
accountSid = '8aaf070866235bc5016653cba34012a7'

# 主帐号Token
accountToken = '9220d802ce8a4d8b956358fb8bf0ebd1'

# 应用Id
appId = '8aaf070866235bc5016653cba3a312ae'

# 请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

# 请求端口
serverPort='8883';

# REST版本号
softVersion='2013-12-26';
# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为列表 例如：['12','34']，如不需替换请填 ''
# @param $tempId 模板Id


class CCP(object):
    # 判断CCP类有没有已经创建好的对象，如果没有，创建一个对象，并且保存
    # 如果有，则将保存的对象直接返回
    __instance = None

    # 创建一个单例模式的对象，用来对对象进行初始化的操作
    def __new__(cls):
        if cls.__instance is None:
            obj = super(CCP, cls).__new__(cls)
            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)
            cls.__instance = obj
        return cls.__instance

    def send_template_sms(self, to, datas, temp_id):
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        # for k, v in result.iteritems():
        #
        #     if k == 'templateSMS':
        #             for k, s in v.iteritems():
        #                 print '%s:%s' % (k, s)
        #     else:
        #         print '%s:%s' % (k, v)
        # return result
        status_code = result.get("statusCode")
        if status_code == "000000":
            # 表示发送成功
            return 0
        else:
            # 表示发送失败
            return -1
   
# sendTemplateSMS(手机号码,内容数据,模板Id)


if __name__ == '__main__':
    cpp = CCP()
    cpp.send_template_sms('13631618442', ['1234', '5'], 1)
    # print(ret)