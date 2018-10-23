# coding=utf-8
import redis


# 按照惯例，配置文件中的变量都使用大写
class Configs(object):
    # 配置文件
    SECRET_KEY = "HFHADSHG12J$%&$##GHJFHJ"
    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:l11556633@127.0.0.1:3306/ihome"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # redis
    REDIS_HOST = '127.0.0.1'
    REDIS_POST = 6379
    # 配置redis，即使用flask-redis,配置它的作用在于实现将session存放在redis中
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_POST)  # 连接数据库
    SESSION_USE_SIGNER = True  # 对cookie中的session_id进行隐藏
    PERMANENT_SESSION_LIFETIME = 86400  # session数据的有效期，单位是秒


class Development(Configs):
    # 当处于开发者模式时
    DEBUG = True


class Production(Configs):
    # 当处于生产运行模式时
    pass


# 在进行项目的配置文件的设置的时候，根据具体的要求来选择具体的键值对
config_map = {
    "develop": Development,
    "product": Production
}