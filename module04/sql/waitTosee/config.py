from datetime import timedelta
from celery.schedules import crontab


CELERY.TIMEZONE = 'Asia/Shanghai'
CELERYBEAT_SCHEDULE = {
    'every-15s-log':{
        'task':'task_log.worker',
        'schedule':crontab(hour=7, minute=30, day_of_week=1),
        'args':('log',)
    }

}