from celery import shared_task
from django.core.mail import send_mail
from fundoo.settings import EMAIL_HOST_USER
from util import static_data


@shared_task
def send_reminder_mail(rem,recipient):
    sub = static_data.REMINDER_SUB
    msg = "You have a reminder in fundoo at {}".format(rem)
    send_mail(sub, msg, EMAIL_HOST_USER, [recipient])
    return None
