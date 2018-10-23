# coding=utf-8


from ihome.libs.yuntongxun.sms import CCP
from ihome.task.main import celery_app


# 发布异步任务
@celery_app.task
def send_sms(to, datas, temp_id):
    cpp = CCP()
    cpp.send_template_sms(to, datas, temp_id)