import datetime

# HR APP SPECIFIC settings ####
EMPLOYMENT_TYPE_CHOICES = (
    ('PE', _('permanent')),
    ('PB', _('probationary')),
    ('IN', _('intern')),
    ('CT', _('contract')),
)

LEAVE_TYPE_CHOICES = (
    ('CL', _('casual')),
    ('PL', _('privilege')),
    ('SL', _('sick')),
    ('WFH', _('workfromhome')),
    ('COMP', _('compensation')),
    ('LOP', _('lossofpay')),
)

DEFAULT_LEAVE_TYPE = 'PL'

LEAVE_STATUS_CHOICES = (
    ('CREATED', _('created')),
    ('SUBMITTED', _('submitted')),
    ('APPROVED', _('approved')),
    ('REJECTED', _('rejected')),
    ('CLOSED', _('closed')),
    ('REOPENED', _('reopened')),
)

LEAVE_DEFAULT_STATUS = 'CREATED'

#WORKING_DAY_START = datetime.time(9, 0)
#WORKING_DAY_END = datetime.time(18, 30)

#LAUNCH_TIME_START = datetime.time(13, 0)
#LAUNCH_TIME_END = datetime.time(14, 30)

#EXPENSE_TYPE_CHOICES = (
#    ('TRV', _('travel')),
#    ('MDC', _('medical')),
#    ('FOD', _('food')),
#    ('CAL', _('call')),
#    ('OTH', _('others')),
#)

#DEFAULT_EXPENSE_TYPE = 'TRV'

