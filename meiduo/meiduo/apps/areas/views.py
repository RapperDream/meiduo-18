from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, GenericAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas.models import Area, Address
from areas.serializers import AreaSerializer, AddressSerializer

# 省信息
from users.models import User


class AreaView(ListAPIView):
    queryset = Area.objects.filter(parent=None)
    serializer_class = AreaSerializer


# 市信息
class AreasView(ListAPIView, CacheResponseMixin):
    serializer_class = AreaSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Area.objects.filter(parent=pk)


# 地址的增删改查
class AddressView(ListCreateAPIView, UpdateAPIView):
    serializer_class = AddressSerializer

    # queryset = Address.objects.filter(user=user)  # 此处获取不到user所以重写
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_deleted=False)

    def get(self, request, *args, **kwargs):
        address = self.get_queryset()
        default_address_id = request.user.default_address_id
        ser = self.get_serializer(address, many=True)
        return Response({'default_address_id': default_address_id, 'address': address})

    def delete(self, request, pk):
        address = self.get_object()
        address.is_deleted = True
        address.save()

        return Response({"message": "ok"})


class StatusView(GenericAPIView):
    def put(self, request, pk):
        user = request.user
        user.default_address_id = pk
        user.save()

        # 返回序列化器对象
        address = Address.objects.get(id=pk)
        ser = AddressSerializer(address)

        return Response(ser.data)
