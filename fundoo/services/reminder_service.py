from datetime import datetime
from note.models import Note
from django.contrib.auth.models import User
import pytz

ITZ = pytz.timezone('Asia/Kolkata')

def check_reminder_for_upcoming_time(reminder):
    if reminder == None:
        raise KeyError
    split_date = reminder[0:10]
    split_time = reminder[-5:]
    date = datetime.now(ITZ).date()
    time = datetime.now(ITZ).time()
    if not (str(date) > split_date or (str(date) == split_date and str(time) > split_time)):
        return True
    return False

def get_note_reminders():
    all_reminder = []
    try:
        reminder_note = Note.objects.filter(trash=False).exclude(reminder=None)
        date = datetime.now(ITZ).strftime("%m/%d/%Y")
        time = datetime.now(ITZ).strftime("%H:%M")
        for note in reminder_note:
            reminder = note.reminder
            reminder_date = reminder.strftime("%m/%d/%Y")
            reminder_time = reminder.strftime("%H:%M")
            timedelta = int(reminder_time[0:2]) - int(time[0:2])
            if(date == reminder_date) and (timedelta == 1 or timedelta == 0):
                user = User.objects.get(id=note.user_id)
                email = user.email
                all_reminder.append([reminder_time, email])
        return all_reminder
    except Exception as e:
        return []