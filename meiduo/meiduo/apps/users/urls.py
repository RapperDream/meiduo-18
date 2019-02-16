from django.conf.urls import url

from users import views

urlpatterns = [
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/', views.SmsCode.as_view()),
]
