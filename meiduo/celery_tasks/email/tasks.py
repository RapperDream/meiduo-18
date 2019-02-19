from django.conf import settings
from django.core.mail import send_mail

from celery_tasks.main import app


@app.task(name='send_email')
def send_email(to_email, verify_html):
    send_mail('美多商城验证', '', settings.EMAIL_FROM, [to_email], html_message=verify_html)
