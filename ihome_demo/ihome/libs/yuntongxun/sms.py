# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from CCPRestSDK import REST
import ConfigParser

# ���ʺ�
accountSid = '8aaf070866235bc5016653cba34012a7'

# ���ʺ�Token
accountToken = '9220d802ce8a4d8b956358fb8bf0ebd1'

# Ӧ��Id
appId = '8aaf070866235bc5016653cba3a312ae'

# �����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

# ����˿�
serverPort='8883';

# REST�汾��
softVersion='2013-12-26';
# ����ģ�����
# @param to �ֻ�����
# @param datas �������� ��ʽΪ�б� ���磺['12','34']���粻���滻���� ''
# @param $tempId ģ��Id


class CCP(object):
    # �ж�CCP����û���Ѿ������õĶ������û�У�����һ�����󣬲��ұ���
    # ����У��򽫱���Ķ���ֱ�ӷ���
    __instance = None

    # ����һ������ģʽ�Ķ��������Զ�����г�ʼ���Ĳ���
    def __new__(cls):
        if cls.__instance is None:
            obj = super(CCP, cls).__new__(cls)
            # ��ʼ��REST SDK
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
            # ��ʾ���ͳɹ�
            return 0
        else:
            # ��ʾ����ʧ��
            return -1
   
# sendTemplateSMS(�ֻ�����,��������,ģ��Id)


if __name__ == '__main__':
    cpp = CCP()
    cpp.send_template_sms('13631618442', ['1234', '5'], 1)
    # print(ret)