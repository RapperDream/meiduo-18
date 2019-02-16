from django.conf.urls import url

from users import views

urlpatterns = [
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/', views.SmsCode.as_view()),
    url(r'^usernames/(?P<username>\w+)/count/', views.UserNameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/', views.MobileCountView.as_view()),
    url(r'^users/', views.UserView.as_view())
]
