from django.conf.urls import url

from areas import views

urlpatterns = [
    url(r'^areas/$', views.AreaView.as_view()),
    url(r'^areas/(?P<pk>\d+)/$', views.AreasView.as_view()),
    url(r'^addresses/$', views.AddressView.as_view()),
]