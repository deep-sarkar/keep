from celery import shared_task
from django.core.mail import send_mail
from fundoo.settings import EMAIL_HOST_USER
from time import sleep

@shared_task
def send_fundoo_mail(sub, msg, recipient):
    send_mail(sub, msg, EMAIL_HOST_USER, recipient)
    return None
