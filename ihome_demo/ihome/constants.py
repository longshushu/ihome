# coding=utf-8

# 图片验证码的redis有效期, 单位：秒
IMAGE_CODE_REDIS_EXPIRES = 180
SMS_CODE_REDIS_EXPIRES = 300
SEND_SMS_CODE_REDIS_EXPIRES = 60
# 设置登录时错误的最大次数
LOGIN_ERROR_MAX_TIMES = 5
# 错误次数信息的有效期设置 单位：秒
LOGIN_ERROR_FORBID_TIME = 600
# 设置城区信息在redis中的存储的有效期 单位：秒
AREA_INFO_REDIS_CACHE_EXPIRES = 600
# 设置主页每次返回的房屋的订单数最多的房屋的数量
HOME_PAGE_MAX_HOUSES = 5
# 将主页的房屋的信息存放在redis中的有效期
HOME_PAGE_DATA_REDIS_EXPIRES = 7200
# 房屋详情页面显示的最多的评论页数
HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 20
# 设置房屋信息在REDIS中保存的有效期
HOUSE_DETAIL_REDIS_EXPIRE_SECOND = 7200
# 在房屋列表查询的时候每一页返回多少条数据
HOUSE_LIST_PAGE_CAPACITY = 2
# 房屋列表信息存储的有效期
HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES = 7200
# 跳转到的支付宝的支付网址
ALIPAY_URL_PREFIX = "https://openapi.alipaydev.com/gateway.do?"