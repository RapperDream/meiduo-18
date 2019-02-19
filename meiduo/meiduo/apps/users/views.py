from django.conf import settings
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from random import randint
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from celery_tasks.sms.tasks import send_sms_code
from meiduo.libs.yuntongxun.sms import CCP

# 短信验证码接口
from users.models import User
from users.serializers import UserSerializers, UserDetailSerializer, EmailSerializer


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


class UserNameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return Response(
            {"count": count}
        )


class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return Response(
            {"count": count}
        )


class UserView(CreateAPIView):
    serializer_class = UserSerializers


class UserDetailView(RetrieveAPIView):
    # def get(self, request): # self的属性request, args, kwargs
    #     # 获取用户对象
    #     user = request.user  # 前端返回ｔｏｋｅｎ数据时jwt会自动查询出user对象到request中
    #
    #     # 序列化返回
    #     ser = UserDetailSerializer(user)
    #     return Response(ser.data)
    serializer_class = UserDetailSerializer

    # queryset = User.objects.all() # 设置查询集get_object会匹配路由的pk值，所以要重写
    def get_object(self):
        return self.request.user


class UserEmailView(UpdateAPIView):
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user


class VerifyEmailView(APIView):
    def get(self, request):
        # 获取ｔｏｋｅｎ数据,并解密
        token = request.query_params.get('token', None)
        if token is None:
            return Response({'errors': '缺少token值'}, status=400)

        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            token = tjs.loads(token)
        except:
            return Response({"errors": "无效token"}, status=400)

        # 查询用户
        id = token.get("id")
        print(id)
        user = User.objects.get(id=id)

        # 更新验证状态
        user.email_active = True
        user.save()

        return Response({"message": "ok"})
