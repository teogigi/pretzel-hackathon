import time
from datetime import date, datetime, timedelta

def get_datetime(ts):
    ts = float(ts)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
    slacktime = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    print(slacktime)
    if datetime.now() > (slacktime + timedelta(minutes=1)):
        return True
    return False