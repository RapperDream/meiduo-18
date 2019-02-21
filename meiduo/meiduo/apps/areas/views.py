from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas.models import Area
from areas.serializers import AreaSerializer, AddressSerializer


# 省信息
class AreaView(ListAPIView):
    queryset = Area.objects.filter(parent=None)
    serializer_class = AreaSerializer


# 市信息
class AreasView(ListAPIView, CacheResponseMixin):
    serializer_class = AreaSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Area.objects.filter(parent=pk)

class AddressView(CreateAPIView):
    serializer_class = AddressSerializer