from rest_framework import serializers

from areas.models import Area, Address


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    # 此序列器外键字段是以ｉｄ形式展示的，所以需要修改
    province = serializers.StringRelatedField(label='省', read_only=True)
    city = serializers.StringRelatedField(label='市', read_only=True)
    district = serializers.StringRelatedField(label='区', read_only=True)

    # 用于序列化输入
    province_id = serializers.IntegerField(label='省', write_only=True)
    city_id = serializers.IntegerField(label='市', write_only=True)
    district_id = serializers.IntegerField(label='区', write_only=True)

    class Meta:
        model = Address
        # fields = "__all__"
        exclude = ("user",)

    def create(self, validated_data):
        # 获取user对象
        user = self.context["request"].user
        validated_data['user'] = user

        user = super().create(validated_data)
        return user
