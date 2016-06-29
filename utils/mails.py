from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.models import User
from django.conf import settings
from hr.models import Country, Organization, Holidays
from hr.models import EmployeesDirectory, Department, EmploymentHistory, LeaveAccurals, Leaves
from hr.forms import countryForm, organizationForm, holidaysForm
from hr.forms import employeeForm, leaveRequestForm, leaveEditForm, leaveAccuralForm, singleEmployeeLeaveAccuralForm, csvImportLeaveAccuralForm
from hr.tables import EmployeesTable
import inspect

def create_and_send_html_email(subject, mailBody, useDefaultFrom, toList, ccList):
	funcName = inspect.stack()[0][3]
	bccList = ['noreply@embedur.com']

	# Working Code Disabling Mail Capability for development
	if settings.MAIL_ENABLE:
		try:
			email = EmailMessage(subject, mailBody, useDefaultFrom,
            					toList, bccList, cc=ccList)
			email.content_subtype = "html"
			email.send(fail_silently=False)
			print("[%s] Mail sent successfully." % (funcName))
		except:
			print("[%s] Mail Send Failed." % (funcName))
	else:
		print("[%s] Mail capability DISABLED" % (funcName))

def create_and_send_text_email(subject, mailBody, useDefaultFrom, toList, ccList):
	funcName = inspect.stack()[0][3]
	bccList = ['noreply@embedur.com']

	# Working Code Disabling Mail Capability for development
	if settings.MAIL_ENABLE:
		try:
			email = EmailMessage(subject, mailBody, useDefaultFrom,
            					toList, bccList, cc=ccList)
			email.send(fail_silently=False)
			print("[%s] Mail sent successfully." % (funcName))
		except:
			print("[%s] Mail Send Failed." % (funcName))
	else:
		print("[%s] Mail capability DISABLED" % (funcName))

def create_subject_for_leave_request(leaveObj):
	if leaveObj.numberOfDays == 1:
		subject = "Leave Request from %s for %s day between %s and %s" % (leaveObj.employee_id, leaveObj.numberOfDays, leaveObj.startedDate, leaveObj.endDate)
	else:
		subject = "Leave Request from %s for %s days between %s and %s" % (leaveObj.employee_id, leaveObj.numberOfDays, leaveObj.startedDate, leaveObj.endDate)
	return subject

def create_subject_for_leave_approved_rejected(leaveObj):
	if leaveObj.status == "APPROVED":
		subject = "Approved Leave for %s day between %s and %s" % (leaveObj.numberOfDays, leaveObj.startedDate, leaveObj.endDate)
	elif leaveObj.status == "REJECTED":
		subject = "Rejected Leave for %s day between %s and %s" % (leaveObj.numberOfDays, leaveObj.startedDate, leaveObj.endDate)
	return subject


def create_mailbody_for_leave_request(leaveObj):
	body = "<p>Dear %s, \
			<br><br>\
			<b><u>Leave Details</u></b>\
			<br><br>\
			Employee 	: %s<br> \
			Leave Type 	: %s<br> \
			Date From 	: %s<br> \
			Date To 	: %s<br> \
			Days 		: %s<br> \
			Reason 		: %s<br> \
			<br><br>Please Login to <a href='#'>Internal-Portal</a> to validate the request.\
			<br><br> \
			Thanks,<br> \
			HR Admin (Internal-Portal)\
			</p>"  % (leaveObj.employee_id.manager,
					  leaveObj.employee_id,
					  leaveObj.leaveType,
					  leaveObj.startedDate, 
					  leaveObj.endDate, 
					  leaveObj.numberOfDays,
					  leaveObj.reason) 
	return body

def create_mailbody_for_leave_approved_rejected(leaveObj):
	if leaveObj.status == "APPROVED":
		status = "APPROVED"
	elif leaveObj.status == "REJECTED":
		status = "REJECTED"
	else:
		status = "APPROVED"
	body = "<p>Dear %s, \
			<br><br>\
			Your leave has been <b><u>%s</u></b>.\
			<br><br>\
			<b><u>Leave Details</u></b> \
			<br><br>\
			Leave Type 	: %s<br> \
			Date From 	: %s<br> \
			Date To 	: %s<br> \
			Days 		: %s<br> \
			Reason 		: %s<br> \
			<br><br>Please Login to <a href='#'>Internal-Portal</a> to validate the request.\
			<br><br> \
			Thanks,<br> \
			HR Admin (Internal-Portal)\
			</p>"  % (leaveObj.employee_id,
					  status,
					  leaveObj.leaveType,
					  leaveObj.startedDate, 
					  leaveObj.endDate, 
					  leaveObj.numberOfDays,
					  leaveObj.reason) 
	return body

def create_toList_for_leave_request(leaveObj):
	toList = []
	if leaveObj.employee_id.manager:
		toList.append(leaveObj.employee_id.manager.email)
	else:
		toList.append('venkateshm@embedur.com')

	# Need to add if any required in future
	return toList

def create_toList_for_leave_approved_rejected(leaveObj):
	toList = []
	toList.append(leaveObj.employee_id.email)
	
	# Need to add if any required in future
	return toList

def create_ccList_for_leave_request(leaveObj):
	ccList = []
	ccList.append(leaveObj.employee_id.email)
	# Need to add if any required in future say HR Admin role i.e. Venkatesh
	if leaveObj.employee_id.manager:
		ccList.append('venkateshm@embedur.com')
	else:
		pass
	return ccList

def create_ccList_for_leave_approved_rejected(leaveObj):
	ccList = []
	# Need to add if any required in future say HR Admin role i.e. Venkatesh
	if leaveObj.employee_id.manager:
		ccList.append(leaveObj.employee_id.manager.email)
	ccList.append('venkateshm@embedur.com')
	return ccList

def _process_mail_for_leave_request(leaveObj, mailContentType):
	if mailContentType == 'html':
		create_and_send_html_email(create_subject_for_leave_request(leaveObj),
									create_mailbody_for_leave_request(leaveObj),
									settings.DEFAULT_FROM_EMAIL,
									create_toList_for_leave_request(leaveObj),
									create_ccList_for_leave_request(leaveObj)
									)
	else:
		create_and_send_text_email(create_subject_for_leave_request(leaveObj),
									create_mailbody_for_leave_request(leaveObj),
									settings.DEFAULT_FROM_EMAIL,
									create_toList_for_leave_request(leaveObj),
									create_ccList_for_leave_request(leaveObj)
									)

def _process_mail_for_leave_approved_rejected(leaveObj, mailContentType):
	if mailContentType == 'html':
		create_and_send_html_email(create_subject_for_leave_approved_rejected(leaveObj),
									create_mailbody_for_leave_approved_rejected(leaveObj),
									settings.DEFAULT_FROM_EMAIL,
									create_toList_for_leave_approved_rejected(leaveObj),
									create_ccList_for_leave_approved_rejected(leaveObj)
									)
	else:
		create_and_send_text_email(create_subject_for_leave_approved_rejected(leaveObj),
									create_mailbody_for_leave_approved_rejected(leaveObj),
									settings.DEFAULT_FROM_EMAIL,
									create_toList_for_leave_approved_rejected(leaveObj),
									create_ccList_for_leave_approved_rejected(leaveObj)
									)

