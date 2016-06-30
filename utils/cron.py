from django.conf import settings
from django_cron import CronJobBase, Schedule
from hr.models import EmployeesDirectory, LeaveAccurals, Leaves
from utils.mails import create_and_send_html_email, create_and_send_text_email

class EmailSendCronJob(CronJobBase):
    """
    Send an email with the user count.
    """
    RUN_EVERY_MINS = 10 if settings.DEBUG else 360   # 6 hours when not DEBUG

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron.EmailSendCronJob'

    def do(self):
        message = 'Hey Aravindh, Scheduled Task'
        ccList = []
        ccList.append('venkateshm@embedur.com')
        toList = []
        toList.append('aravindhd@embedur.com')
        print(message)
        create_and_send_text_email('[django-cron demo] Active user count',
                                    message,
                                    settings.DEFAULT_FROM_EMAIL,
                                    toList,
                                    ccList)