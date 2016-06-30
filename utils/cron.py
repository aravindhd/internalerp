from django.conf import settings
from hr.models import EmployeesDirectory, LeaveAccurals, Leaves
from utils.mails import create_and_send_html_email, create_and_send_text_email

def SendLeavesToApproveEmail():
    '''
    Send email to Managers about the pending leaves to approve/reject
    '''
    ccList = []
    ccList.append(settings.DEFAULT_CC_EMAIL)
    mgrList = EmployeesDirectory.objects.filter(is_manager=True)
    for mgr in mgrList:
        sendMail = False
        toList = []
        head = "<p>Dear %s, \
                   <br><br>\
                   Please update the following leaves submitted to you.<br><br>\
                   <table>\
                    <thead>\
                        <td>Employee</td>\
                        <td>Leave Type</td>\
                        <td>Start Date</td>\
                        <td>End Date</td>\
                        <td>No. of Days</td>\
                    </thead>\
                    <tbody>"  % (mgr)
        bottom = "</tbody></table> \
            Please Login to <a href='#'>Internal-Portal</a> to validate the request.\
            <br><br> \
            Thanks,<br> \
            HR Admin (Internal-Portal)\
            </p>"
        toList.append(mgr.email)
        rows = []
        leavesList = Leaves.objects.filter(employee_id__manager=mgr)
        for leave in leavesList:
            if (leave.status == 'SUBMITTED') or (leave.status == 'REOPENED'):
                print(leave)
                sendMail = True
                rows.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" 
                            % ( leave.employee_id, 
                                leave.leaveType, 
                                leave.startedDate, 
                                leave.endDate, 
                                leave.numberOfDays))
        message = head + ''.join(rows) + bottom
        if sendMail:
            create_and_send_html_email('Leaves requiring your Update!',
                                        message,
                                        settings.DEFAULT_FROM_EMAIL,
                                        toList,
                                        ccList)
        else:
            pass
    print("Processed Scheduled Task for Leaves!!")