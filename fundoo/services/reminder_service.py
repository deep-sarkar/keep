from datetime import datetime


def check_reminder_for_upcoming_time(reminder):
    split_date = reminder[0:10]
    split_time = reminder[-5:]
    date = datetime.now().date()
    time = datetime.now().time()
    if not (str(date) > split_date or (str(date) == split_date and str(time) > split_time)):
        return True
    return False


