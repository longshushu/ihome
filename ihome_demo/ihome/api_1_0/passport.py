# coding=utf-8


from ihome.api_1_0 import api
from ihome import redis_store, db, constants
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
import re
from ihome.models import User
from sqlalchemy.exc import IdentifierError


# post 请求方式
# api/v1.0/register     需要传的参数包括短信验证码，用户名，用户名密码，确认的密码
@api.route("/register", methods=["POST"])
def register():
    # 1 获取参数 传来的参数的格式为json的格式，方式为POST的方式
    """
    请求的参数： 手机号、短信验证码、密码、确认密码
    参数格式：json
    :return:
    """
    # 将得到的json数据转化为字典的形式
    req_dict = request.get_json()
    sms_code = req_dict.get("sms_code")
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")
    # 确认参数的完整性
    if not all([sms_code, mobile, password, password2]):
        return jsonify(errno=RET.DATAERR, errmsg="参数不完整")
    # 2 校验参数
    # 3 进行业务逻辑的判断
    # 判断手机格式是否正确
    if not re.match(r'1[34578]\d{9}', mobile):
        # 表示手机 的格式不正确
        return jsonify(errno=RET.PARAMERR, errmsg="手机格式错误")
    # 判断两次密码是否一致
    if password2 != password:
        return jsonify(errno=RET.PWDERR, errmsg="两次密码不一致")
    # 从redis中读取短信验证码进行校验
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="读取真实短信验证码时数据库连接异常")
    # 判断验证码是否过期
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已经过期")
    # 将redis中的短信验证码的数据进行删除，防止进行同一个验证码的重复使用
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    # 判断用户填写的验证码的正确性
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入有误")
    # 判断用户的手机号是否注册过
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    # else:
    #     if user is not None:
    #         # 表示手机号已存在
    #         return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")

    # 盐值   salt

    #  注册
    #  用户1   password="123456" + "abc"   sha1   abc$hxosifodfdoshfosdhfso
    #  用户2   password="123456" + "def"   sha1   def$dfhsoicoshdoshfosidfs
    #
    # 用户登录  password ="123456"  "abc"  sha256      sha1   hxosufodsofdihsofho
    # 将用户保存到数据库中
    # 在这里可以使用property进行将一个函数转化为一个类的属性，具体的定义是在models中进行的
    user = User(name=mobile, mobile=mobile)
    user.password = password
    # 将变化保存在数据库中
    try:
        db.session.add(user)
        db.session.commit()
    except IdentifierError as e:
        db.session.rollback()
        # 表示手机号码已经注册过
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号码已经注册过了")
    except Exception as e:
        db.session.rollback(e)
        current_app.logger.error(3)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询异常")
    # 保存状态到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session ["user_id"] = user.id
    # 4 返回值
    return jsonify(errno=RET.OK, errmsg="注册成功")


# 进行用户的登录操作
# 对应的登录的视图函数 使用的请求方式应该是POST
# @api.route("/api/v1.0/login")
@api.route("/login", methods=["POST"])
def login():
    """
    需要得到的参数为用户的用户名和密码
    :return:
    """
    # 获取参数
    # 要求传来的参数的格式为json的格式
    rep_dic = request.get_json()
    mobile = rep_dic.get("mobile")
    password = rep_dic.get("password")
    # 进行参数的完整性的校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="请求参数不完整")
    # 进行手机格式的校验
    if  not re.match(r'1[34578]\d{9}', mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机格式不正确")
    # 限制密码错误的次数,当错误次数达到一定的次数后则返回
    # redis 记录 "access_nums_请求的ip": "次数"
    access_ip = request.remote_addr  # 可以通过此来获取用户的Ip
    # 获取redis中该用户的错误次数
    try:
        access_nums = redis_store.get("access_num_%s" % access_ip)
    except Exception as e:
        current_app.logger.error(e)
    # 将得到的错误次数与设定的最大次数进行对比
    if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
        return jsonify(errno=RET.REQERR, errmsg="错误次数超过限制，请稍后再试")
    # 从数据库中取出手机号对应的密码进行比较
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息时数据库请求异常")
    if user is None and not user.check_login(password):
        # 如果验证失败则将错误错误次数记录
        # redis的incr可以对字符串类型的数字数据进行加一操作，如果数据一开始不存在，则会初始化为1
        try:
            redis_store.incr("access_num_%s" % access_ip)
            redis_store.expire("access_num_%s" % access_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")
    # 验证成功，保存登录状态到session中
    session["mobile"] = user.mobile
    session["user_id"] = user.id
    session["name"] = user.name
    return jsonify(errno=RET.OK, errmsg="登录成功")


# 确认用户的登录状态
@api.route("/session", methods=["GET"])
def check_login():
    # 检查登录状态
    # 尝试从session中读取用户的姓名
    name = session.get("name")
    # 如果session中能够拿到数据说明用户已经登录，否则判断用户未进行登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


# 用户退出登录，将session删除
@api.route("/session", methods=["DELETE"])
def logout():
    session.clear()
    return jsonify(errno=RET.OK, errmsg="OK")