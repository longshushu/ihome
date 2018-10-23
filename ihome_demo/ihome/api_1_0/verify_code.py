# coding=utf-8

from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants, db
from ihome.models import User
from flask import jsonify, current_app, make_response
from ihome.utils.response_code import RET
from flask import request
import random
from ihome.libs.yuntongxun.sms import CCP
from ihome.task.sms.tasks import send_sms


# GET 127.0.0.1/api/v1.0/image_codes/<image_code_id>
@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    # 获取图片验证码的视图
    """
    : params
    image_code_id:  图片验证码编号
    :return:  正常:验证码图片
    异常：返回json
    """
    # 业务逻辑处理
    # 生成验证码图片
    # 名字，真实文本， 图片数据
    name, text, image_data = captcha.generate_captcha()
    # 进行redis的设置
    # redis：  字符串   列表  哈希   set
    # 1 使用hash的字段进行存储,在设置有效期的时候只能整体的设置，不方便操作
    # hset image_codes:{id1:"abc", id2:"123"}
    # 2 使用字符串单独设置
    # set image_codes_编号1:真实值
    # set_image_codes_编号2：真实值
    # redis_store.set("image_codes_%s" % image_code_id, text)
    # redis_store.set("image_codes_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES)
    # 可以将上面两句话合并为一句话
    try:
        redis_store.setex("image_codes_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 设置日志log
        current_app.logger.error(e)
        # 将错误信息返回
        return jsonify(errno=RET.DBERR, errmsg="save image code id failed")
    # return make_response(image_data) 因为返回的时候不设置返回数据的格式的话，默认返回的是text/html
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


# 图片验证码的获取
# get /api/v1.0/<mobile>/?image_code = xxx  image_code_id
@api.route("/sms_code/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    # 获取短信验证码
    """
    :param mobile: 手机号码
    :return: 正常返回一个Json数据，异常返回异常
    """
    # 1、获取参数
    # 获取图片验证码的内容和图片验证码的ID
    # print (11111)
    # image_code = request.args.get("image_code")
    # image_code_id = request.args.get("image_code_id")
    # # 2、参数的校验
    # # 判断参数的完整性
    # if not all([image_code_id, image_code]):
    #     return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # # 校验验证码的有效性
    # try:
    #     real_image_code = redis_store.get("image_codes_%s" % image_code_id)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="数据库连接异常")
    # if real_image_code is None:
    #     return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")
    # # 删除redis中的图片验证码，防止用户使用同一个图片验证码验证多次
    # try:
    #     redis_store.delete("image_code_%s" % image_code_id)
    # except Exception as e:
    #     current_app.logger.error(e)
    # # 3、相应的业务逻辑处理
    # # 进行图片验证码的对比
    # if real_image_code.lower() != image_code.lower():
    #     return jsonify(errno=RET.DBERR, errmsg="图片验证码错误")
    # # 判断对于这个手机号的操作，在60秒内有没有之前的记录，如果有，则认为用户操作频繁，不接受处理
    # try:
    #     send_flag = redis_store.get("send_sms_code_%s" % mobile)
    # except Exception as e:
    #     current_app.logger.error(e)
    # else:
    #     # 表示在60秒内之前有过发送的记录
    #     if send_flag is not None:
    #         return jsonify(errno=RET.REQERR, errmsg="请求过于频繁，请60s后再发送")
    # # 进行手机的校验，判断手机是否已经存在
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    # else:
    #     if user is not None:
    #         return jsonify(errno=RET.DATAEXIST, errmsg="用户已经存在，可以直接登录")
    # # 生成短信验证码
    # sms_code = "%06d" % random.randint(0, 999999)
    # try:
    #     # 保存手机号的id到redis中
    #     redis_store.setex("sms_code_%s" % mobile , constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    #     # 将发送短信的记录保存到REDIS中，防止用户在60秒内频繁的发送短信
    #     redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_REDIS_EXPIRES, 1)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="保存数据异常")
    # # 发送短信验证码
    # try:
    #     ccp = CCP()
    #     result = ccp.send_template_sms(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES)/60], 1)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    #
    # # 4、 返回值
    # if result == 0:
    #     return jsonify(errno=RET.OK, errmsg="发送成功")
    # else:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送失败")

    # 使用celery进行异任务的操作
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")
    # 2、参数的校验
    # 判断参数的完整性
    if not all([image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 校验验证码的有效性
    try:
        real_image_code = redis_store.get("image_codes_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库连接异常")
    if real_image_code is None:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")
    # 删除redis中的图片验证码，防止用户使用同一个图片验证码验证多次
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 3、相应的业务逻辑处理
    # 进行图片验证码的对比
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DBERR, errmsg="图片验证码错误")
    # 判断对于这个手机号的操作，在60秒内有没有之前的记录，如果有，则认为用户操作频繁，不接受处理
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        # 表示在60秒内之前有过发送的记录
        if send_flag is not None:
            return jsonify(errno=RET.REQERR, errmsg="请求过于频繁，请60s后再发送")
    # 进行手机的校验，判断手机是否已经存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg="用户已经存在，可以直接登录")
    # 生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)
    try:
        # 保存手机号的id到redis中
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 将发送短信的记录保存到REDIS中，防止用户在60秒内频繁的发送短信
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_REDIS_EXPIRES, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据异常")
    # # 发送短信验证码
    # try:
    #     ccp = CCP()
    #     result = ccp.send_template_sms(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES) / 60], 1)
    result_obj = send_sms.delay(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES) / 60], 1)
    print(result_obj.id)

    # 通过异步任务对象的get方法获取异步任务的结果, 默认get方法是阻塞的
    ret = result_obj.get()
    print("ret=%s" % ret)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="发送成功")
    # 4、 返回值
    # if result == 0:
    #     return jsonify(errno=RET.OK, errmsg="发送成功")
    # else:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送失败")

