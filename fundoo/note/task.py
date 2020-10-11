from celery import shared_task
from django.core.mail import send_mail
from fundoo.settings import EMAIL_HOST_USER
from util import static_data
from services.reminder_service import get_note_reminders


@shared_task
def send_reminder_mail(rem,recipient):
    sub = static_data.REMINDER_SUB
    msg = "You have a reminder in fundoo at {}".format(rem)
    send_mail(sub, msg, EMAIL_HOST_USER, [recipient])
    return None

@shared_task
def send_reminder_notification():
    reminders = get_note_reminders()
    if len(reminders) != 0:
        for reminder in reminders:
            sub = static_data.REMINDER_SUB
            msg = "You have a reminder in fundoo at {}".format(reminder[0])
            send_mail(sub, msg, EMAIL_HOST_USER, [reminder[1]])
    return None

