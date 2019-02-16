from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from random import randint

from celery_tasks.sms.tasks import send_sms_code
from meiduo.libs.yuntongxun.sms import CCP


# 短信验证码接口
class SmsCode(APIView):
    def get(self, request, mobile):
        conn = get_redis_connection('verify')  # redis的操作可以到ｒｅｄｉｓ中国官网查看
        # 控制发送频率,60s
        flag = conn.get('sms_flag_{}'.format(mobile))
        if flag:
            return Response({"errors": "请求过于频繁"}, status=402)

        # 生成一个短信验证码
        sms_code = "%06d" % randint(0, 999999)

        # 保存短信验证码并设置发送频率限制
        pl = conn.pipeline()  # 设置ｒｅｄｉｓ管道，只连接一次提高效率
        pl.setex('sms_{}'.format(mobile), 300, sms_code)
        pl.setex('sms_flag_{}'.format(mobile), 60, 1)
        pl.execute()

        # 发送短信验证码
        send_sms_code.delay(mobile, sms_code)  # 切记是这个方式使用ｃｅｌｅｒｙ
        print(sms_code)  # 使用celery作用是发送短信有延迟，直接跳过执行下面的逻辑

        # 返回结果
        return Response({"message": "ok"})
