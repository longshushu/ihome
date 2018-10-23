# coding=utf-8

from flask import Blueprint, current_app, make_response
from flask_wtf import csrf

html = Blueprint("web_html", __name__)

# 127.0.0.1:5000/()
# 127.0.0.1:5000/(index.html)
# 127.0.0.1:5000/register.html
# 127.0.0.1:5000/favicon.ico   # 浏览器认为的网站标识， 浏览器会自己请求这个资源


@html.route("/<re(r'.*'):html_file_name>")
def get_html(html_file_name):
    # 获取静态页面资源
    if not html_file_name:
        # 如果得到的是空的，就表示获取的是主页
        html_file_name = "index.html"
    if html_file_name != "favicon.ico":
        # 如果请求的不是获取网站标识的路径
        html_file_name = "html/" + html_file_name
    resp = make_response(current_app.send_static_file(html_file_name))
    # 设置csrf防护机制,创建一个csrf_token值
    csrf_token = csrf.generate_csrf()
    # 将csrf_token存到cookie中
    resp.set_cookie("csrf_token", csrf_token)
    return resp
