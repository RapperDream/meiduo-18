from django.conf import settings
from django_redis import get_redis_connection
from rest_framework import serializers
from itsdangerous import JSONWebSignatureSerializer as TJS
from rest_framework_jwt.settings import api_settings

from oauth.models import OAuthQQUser
from users.models import User


class QQAuthUserSerializer(serializers.ModelSerializer):
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    token = serializers.CharField(read_only=True)
    openid = serializers.CharField(write_only=True)
    user_id = serializers.IntegerField(read_only=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')  # 手机号码格式验证

    class Meta:
        model = User
        fields = ('mobile', 'password', 'sms_code', 'token', 'openid', 'username', 'id')
        extra_kwargs = {
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True,
                'error_messages': {
                    'min_length': '密码过短',
                    'max_length': '密码过长'
                }
            },
            'username': {
                'max_length': 20,
                'min_length': 5,
                'read_only': True,
                'error_messages': {
                    'min_length': '用户名过短',
                    'max_length': '用户名过长'
                }
            }
        }

    def validate(self, attrs):
        # 验证openid
        tjs = TJS(settings.SECRET_KEY, 300)

        # 解密
        try:
            data = tjs.loads(attrs['openid'])
        except:
            raise serializers.ValidationError("openid错误")
        openid = data.get('openid')
        attrs['open_id'] = openid

        # 验证短信验证码
        conn = get_redis_connection('verify')

        # 取出验证码
        real_sms = conn.get('sms_{}'.format(attrs["mobile"]))

        # 验证码比对
        if not real_sms:
            raise serializers.ValidationError("验证码已经过期")
        if real_sms.decode() != attrs["sms_code"]:
            raise serializers.ValidationError("验证码不匹配")

        # 验证用户是否注册过
        try:
            user = User.objects.get(mobile=attrs['mobile'])
        except:
            # 用户未注册
            return attrs
        else:
            # 用户已经注册
            # 密码校验
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError("密码不正确")
            attrs['user'] = user
            return attrs

    def create(self, validated_data):
        user = validated_data.get('user', None)
        # 判断是否注册
        if user is None:
            user = User.objects.create_user(username=validated_data['mobile'], password=validated_data['password'],
                                            mobile=validated_data['mobile'])
        OAuthQQUser.objects.create(user=user, openid=validated_data['open_id'])

        # 生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token
        user.user_id = user.id

        return user
