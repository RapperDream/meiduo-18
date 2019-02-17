import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User


class UserSerializers(serializers.ModelSerializer):
    # 显示指明字段
    password2 = serializers.CharField(max_length=20, min_length=8, write_only=True)
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    allow = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)  # 返回token

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'password', 'password2', 'sms_code', 'allow', 'token')
        extra_kwargs = {
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': 'True',
                'error_messages': {
                    'max_length': "密码过长",
                    'min_length': "密码过短"
                },
            },
            'username': {
                'max_length': 20,
                'min_length': 5,
                'error_messages': {
                    'max_length': "昵称过长",
                    'min_length': "昵称过短"
                }
            }
        }

    # 手机号验证
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机格式不正确")
        return value

    # 选中协议状态
    def validate_allow(self, value):
        if value != "true":
            raise serializers.ValidationError("协议未选中")
        return value

    def validate(self, attrs):
        # 密码对比
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("两次密码不匹配")

        # 短信验证码对比
        # 建立ｒｅｄｉｓ连接
        conn = get_redis_connection("verify")

        # 取出验证码
        real_sms = conn.get('sms_{}'.format(attrs["mobile"]))

        # 验证码比对
        if not real_sms:
            raise serializers.ValidationError("验证码已经过期")
        if real_sms.decode() != attrs["sms_code"]:
            raise serializers.ValidationError("验证码不匹配")
        return attrs

    def create(self, validated_data):
        # 删除不需要保存的字段
        del validated_data["password2"]
        del validated_data["allow"]
        del validated_data["sms_code"]
        # user = super().create(validated_data)

        # 自动加密
        # user = User.objects.create_user(username=validated_data["username"])

        # 手动加密
        user = User.objects.create(username=validated_data['username'], mobile=validated_data['mobile'],
                                   password=validated_data['password'])
        user.set_password(validated_data["password"])
        user.save()

        # 生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # 用户对象额外添加token
        user.token = token

        return user
