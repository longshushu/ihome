# coding=utf=8

from ihome.api_1_0 import api
from ihome.utils.commons import RET
from ihome.utils.commons import login_required
from flask import g, current_app, jsonify, request, session
from ihome.models import User
from ihome import db


# 更改用户的用户名
# 需要将参数使用json的方式传过来，同时使用PUT的方式
@api.route("/user/name", methods=["PUT"])
@login_required
def change_user_name():
    # 因为进行了登录校验，可以直接从g对象中取出user_id
    user_id = g.user_id
    # 获取参数
    req_dict = request.get_json()
    # 进行参数的校验
    if req_dict is None:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 取出用户传过来的用户名
    name = req_dict.get("name")
    if name is None:
        return jsonify(errno=RET.NODATA, errmsg="名字不能为空")
    # 进行数据库的查询并且进行更新
    try:
        User.query.filter_by(id=user_id).update({"name": name})
        # 保存用户昵称name，并同时判断name是否重复（利用数据库的唯一索引)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    # 修改session数据中的name字段
    session["name"] = name
    return jsonify(errno=RET.OK, errmsg="修改用户名成功", data={"name": name})


# 获取用户的信息
@api.route("/user", methods=["GET"])
@login_required
def get_user_profile():
    # 因为进行了登录校验，可以直接从g对象中取出user_id
    user_id = g.user_id
    # 根据得到的用户的id在数据库中查询
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")
    if user is None:
        return jsonify(errno=RET.DBERR, errmsg="无效的操作")
    return jsonify(errno=RET.OK, errmsg="ok", data=user.to_dict())


# 获取实名认证的信息
@api.route("/user/auth", methods=["GET"])
@login_required
def get_user_auth():
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户实名信息失败")
    if user is None:
        return jsonify(errno=RET.DBERR, errmsg="无效的操作")
    return jsonify(errno=RET.OK, errmsg="ok", data=user.auth_to_dict())


# 提交实名认证的信息
@api.route("/user/auth", methods=["POST"])
@login_required
def set_user_auth():
    # 获取参数,即传过来的信息
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    real_name = req_data.get("real_name")
    id_card = req_data.get("id_card")
    # 校验参数的完整性
    if not all([real_name, id_card]):
        return jsonify(errno=RET.DATAERR, errmsg="参数不完整")
    user_id = g.user_id
    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None).update({"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DATAERR, errmsg="保存实名信息失败")
    return jsonify(errno=RET.OK, errmsg="ok")