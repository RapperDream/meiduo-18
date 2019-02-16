import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        "token": token,
        "username": user.username,
        "user_id": user.id
    }


class UsernameMobileAuthBackend(ModelBackend):
    # 重写django原有的登录验证方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 判断username格式
            if re.match(r'^1[3-9]\d{9}$', username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)
        except:
            user = None
        if user is not None and user.check_password(password):
            return user
