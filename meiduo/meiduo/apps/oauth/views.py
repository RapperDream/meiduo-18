from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from itsdangerous import JSONWebSignatureSerializer as TJS

from oauth.models import OAuthQQUser


class QQAuthURLView(APIView):
    def get(self, request):
        # 获取state
        state = request.query_params.get("state", None)  # next表示扫码完成后跳转到美多哪个页面
        if not state:
            state = "/"

        # 调用ｑｑ对象生成跳转链接
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI, state=state)
        login_url = qq.get_qq_url()

        # 返回跳转链接
        return Response({"login_url": login_url})


class QQAuthUserView(CreateAPIView):
    def get(self, request):
        # 获取ｃｏｄｅ数据
        code = request.query_params.get("code", None)
        if code is None:
            return Response({"message": "缺少code值"}, status=400)

        # 通过ｃｏｄｅ值请求ｑｑ服务器获取access_token值
        state = "/"
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI, state=state)
        access_token = qq.get_access_token(code)

        # 通过access_token值请求qq服务器获取openid值
        openid = qq.get_open_id(access_token)

        # 判断openid值是否绑定过美多
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        # 未绑定进行绑定操作
        except:
            # 对openid进行加密
            tjs = TJS(settings.SECRET_KEY, 300)
            open_id = tjs.dumps({'openid': openid}).decode()

            return Response({"openid": open_id})
        # 已经绑定登录成功
        else:
            user = qq_user.user
            # 生成token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            return Response({
                'token': token,
                'username': user.username,
                'user_id': user.id
            })
