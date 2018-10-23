# coding=utf-8

from celery import Celery
from ihome.task import config

# 创建celery对象
celery_app = Celery("ihome")
# 设置配置文件
celery_app.config_from_object(config)
# 设置自动查询搜寻异步任务
celery_app.autodiscover_tasks(["ihome.task.sms"])