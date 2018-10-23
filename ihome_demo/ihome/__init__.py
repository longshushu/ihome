# coding=utf-8
from flask import Flask
from configs import config_map
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
import redis
from ihome.utils.commons import ReConvert


db = SQLAlchemy()  # 由于数据库不仅仅在创建app对象的时候要用，在很多地方都需要用到，如果直接将其放到创建app
# 对象的时候再创建，其他地方就不能导入了，但是
# 如果在此时就把APP对象与其关联，那么就会导致后面出现循环引用，因此在此时先只创建数据库，不将其与应用对象绑定
# 同样的道理对于REDIS也是一样，因此在此处只建立一个redis的对象，在后面的函数中再进行对其初始化
redis_store = None
# 配置日志信息
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)
# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级


# 利用工厂模式的方法，利用传参数的方式来决定使用的是哪种模式
def create_app(config_name):
    """
    创建flask的应用对象
    :param config_name: str  配置模式的模式的名字 （"develop",  "product"）
    :return:将所得到的对象传出去
    """
    app = Flask(__name__)
    # 根据所处在的阶段决定使用的配置文件
    config_class = config_map.get(config_name)  # 得到现目前所要配置文件的对象
    app.config.from_object(config_class)  # 将配置文件注册到app对象中去
    # 使用app初始化db
    db.init_app(app)
    # 与数据库建立连接
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_POST)
    # 利用flask-session，将session数据保存到redis中
    Session(app)
    # 配置CSRF防护
    CSRFProtect(app)
    # 将自定义的转换器加入到app中
    app.url_map.converters["re"] = ReConvert
    # 注册蓝图
    from ihome import api_1_0  # 在此处导入的原因在于为了避免出现循环引用
    app.register_blueprint(api_1_0.api,  url_prefix="/api/v1.0")
    # 注册获取静态页面的蓝图
    from . import web_html
    app.register_blueprint(web_html.html)
    return app

