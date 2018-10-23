# coding=utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_session import Session
from flask_wtf import CSRFProtect

app = Flask(__nama__)


# 按照惯例，配置文件中的变量都使用大写
class Config(object):
    # 配置文件
    SECRET_KEY = "HFHADSHG12J$%&$##GHJFHJ"
    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:l11556633@127.0.0.1:3306/ihome"
    SQLALCHEMY_TRACK_MODIFICATION = True
    # redis
    REDIS_HOST = 127.0.0.1
    REDIS_POST = 6379
    # 配置redis，即使用flask-redis,配置它的作用在于实现将session存放在redis中
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port= REDIS_POST)  #连接数据库
    SESSION_USE_SIGNER = True  # 对cookie中的session_id进行隐藏
    PERMANENT_SESSION_LIFETIME = 86400  # session数据的有效期，单位是秒
app.config.from_object(Config)
db = SQLAlchemy(app)
# 与数据库建立连接
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_POST)
# 利用flask-session，将session数据保存到redis中
Session(app)
# 配置CSRF防护
CSRFProtect(app)

if __name__ == '__main__':
    app.run()




