from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.db.models import Q
from django.contrib.auth.models import User
from django.conf import settings
from django.forms import inlineformset_factory, modelformset_factory
from .models import EmployeesDirectory, Department, EmploymentHistory, LeaveAccurals, Leaves
from .forms import employeeForm, leaveForm, leaveAccuralForm, singleEmployeeLeaveAccuralForm, csvImportLeaveAccuralForm
from .tables import EmployeesTable
from django_tables2 import RequestConfig
import csv

# Create your views here.

def employees_table(request):
	#if not request.user.is_staff or not request.user.is_superuser:
	#	raise Http404
	if not request.user.is_authenticated():
		return redirect('auth_login')

	empTable = EmployeesTable(EmployeesDirectory.objects.all())
	RequestConfig(request, paginate={ "per_page" : 10 }).configure(empTable)
	context = { 'empList' : empTable }
	return render(request, 'hr/employees_table.html', context)

def employees_list(request):
	#if not request.user.is_staff or not request.user.is_superuser:
	#	raise Http404

	if not request.user.is_authenticated():
		return redirect('auth_login')

	empList = EmployeesDirectory.objects.all()
	
	searchQuery = request.GET.get("searchQueryStr")
	if searchQuery:
		empList = empList.filter(
			Q(firstname__icontains=searchQuery) |
			Q(lastname__icontains=searchQuery) |
			Q(designation__icontains=searchQuery) |
			Q(employee_id__icontains=searchQuery) |
			Q(email__icontains=searchQuery)
			#Q(user__last_name__icontains=searchQuery)
			)
	else:
		pass
		
	paginator = Paginator(empList, settings.DEFAULT_PAGINATOR_RECORDS_PERPAGE)
	page = request.GET.get("page")
	try:
		empList = paginator.page(page)
	except PageNotAnInteger:
		empList = paginator.page(1)
    #except EmptyPage:
    #    empList = paginator.page(paginator.num_pages)
    
	context = { 'empList' : empList } #, 'managersList' : managersList }
	return render(request, 'hr/employees.html', context)

def employee_details(request, id):
	#if not request.user.is_staff or not request.user.is_superuser:
	#	raise Http404
	if not request.user.is_authenticated():
		return redirect('auth_login')

	empInfo = get_object_or_404(EmployeesDirectory, id=id)
	lAccList = LeaveAccurals.objects.filter(employee=empInfo)
	leaveAccuralList = {}
	for acc in lAccList:
		leaveAccuralList['%s'%(acc.leaveType)] = acc.accuredLeaves
	context = { 'empInfo' : empInfo, 'leaveAccuralList' : leaveAccuralList }
	return render(request, 'hr/view_employee.html', context)

def employee_info(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	emp = EmployeesDirectory.objects.filter(user=request.user)
	print (emp)
	print(emp.count())

	if emp.count() > 0 :
		lAccList = LeaveAccurals.objects.filter(employee=emp)

	empInfo = get_object_or_404(EmployeesDirectory, id=emp)

	leaveAccuralList = {}
	for acc in lAccList:
		leaveAccuralList['%s'%(acc.leaveType)] = acc.accuredLeaves

	context = { 'empInfo' : empInfo, 'leaveAccuralList' : leaveAccuralList }
	return render(request, 'hr/view_employee.html', context)

def employee_create(request):
	#if not request.user.is_staff or not request.user.is_superuser:
	#	raise Http404
	if not request.user.is_authenticated():
		return redirect('auth_login')

	empForm = employeeForm(request.POST, request.FILES or None)
	lAccForm = leaveAccuralForm(request.POST or None)
	if empForm.is_valid() and lAccForm.is_valid():
		empData = empForm.cleaned_data
		## Create a user account first with given firstname & lastname 
		## then proceed for creating Employee details
		username = '%s%s' %(empData['firstname'], empData['lastname'][0])
		user = User.objects.create_user(username.lower(), empData['email'], settings.DEFAULT_USER_ACCOUNT_PASSWD)
		user.first_name=empData['firstname']
		user.last_name=empData['lastname']
		user.save()

		# Creating Employee record
		instance = empForm.save(commit=False)
		instance.user = user
		instance.save()

		# Creating Leave Accurals for the new employee record
		data = lAccForm.cleaned_data
		lAcc = instance.leaveaccurals_set.create(leaveType='PL',accuredLeaves=data['pl'])
		lAcc = instance.leaveaccurals_set.create(leaveType='CL',accuredLeaves=data['cl'])
		lAcc = instance.leaveaccurals_set.create(leaveType='SL',accuredLeaves=data['sl'])
		lAcc = instance.leaveaccurals_set.create(leaveType='WFH',accuredLeaves=data['wfh'])
		lAcc = instance.leaveaccurals_set.create(leaveType='LOP',accuredLeaves=data['lop'])
		lAcc = instance.leaveaccurals_set.create(leaveType='COMP',accuredLeaves=data['compoff'])
		
		return redirect('employee_details', id=instance.id)
	else:
		empForm = employeeForm()
		lAccInitData = { 'pl' : 0.00, 'cl' : 0.00, 'sl' : 0.00, 'lop' : 0.00, 'wfh' : 0.00, 'compoff' : 0.00}
		lAccForm = leaveAccuralForm(initial=lAccInitData)

	context = {
		"empForm" : empForm,
		"lAccForm" : lAccForm
	}
	return render(request, 'hr/new_employee.html', context)

def employee_update(request, id):
	#if not request.user.is_staff or not request.user.is_superuser:
	#	raise Http404
	if not request.user.is_authenticated():
		return redirect('auth_login')
		
	instance = get_object_or_404(EmployeesDirectory, id=id)
	empForm = employeeForm(request.POST or None, request.FILES or None, instance=instance)
	leaveAccurals = LeaveAccurals.objects.filter(employee=instance)
	lAccInitData = { 'pl' : 0.00, 'cl' : 0.00, 'sl' : 0.00, 'lop' : 0.00, 'wfh' : 0.00, 'compoff' : 0.00}
	for lAccured in leaveAccurals:
		if lAccured:
			if lAccured.leaveType == 'PL':
				lAccInitData['pl'] = lAccured.accuredLeaves
			elif lAccured.leaveType == 'CL':
				lAccInitData['cl'] = lAccured.accuredLeaves
			elif lAccured.leaveType == 'SL':
				lAccInitData['sl'] = lAccured.accuredLeaves
			elif lAccured.leaveType == 'WFH':
				lAccInitData['wfh'] = lAccured.accuredLeaves
			elif lAccured.leaveType == 'LOP':
				lAccInitData['lop'] = lAccured.accuredLeaves
			elif lAccured.leaveType == 'COMP':
				lAccInitData['compoff'] = lAccured.accuredLeaves
			else:
				pass
		else:
			pass

	lAccForm = leaveAccuralForm(request.POST or None, initial=lAccInitData)

	if empForm.is_valid() and lAccForm.is_valid():
		instance = empForm.save(commit=False)
		instance.save()

		cleanedData = lAccForm.cleaned_data
		changedData = lAccForm.changed_data
		for key in changedData:
			if key == 'pl':
				obj, created = LeaveAccurals.objects.update_or_create(employee=instance, leaveType='PL', defaults={'accuredLeaves':cleanedData['pl']})
				#LeaveAccurals.objects.filter(employee=instance).filter(leaveType="PL").update(accuredLeaves=cleanedData['pl'])
			elif key == 'cl':
				obj, created = LeaveAccurals.objects.update_or_create(employee=instance, leaveType='CL', defaults={'accuredLeaves':cleanedData['cl']})
				#LeaveAccurals.objects.filter(employee=instance).filter(leaveType="CL").update(accuredLeaves=cleanedData['cl'])
			elif key == 'sl':
				obj, created = LeaveAccurals.objects.update_or_create(employee=instance, leaveType='SL', defaults={'accuredLeaves':cleanedData['sl']})
				#LeaveAccurals.objects.filter(employee=instance).filter(leaveType="SL").update(accuredLeaves=cleanedData['sl'])	
			elif key == 'wfh':
				obj, created = LeaveAccurals.objects.update_or_create(employee=instance, leaveType='WFH', defaults={'accuredLeaves':cleanedData['wfh']})
				#LeaveAccurals.objects.filter(employee=instance).filter(leaveType="WFH").update(accuredLeaves=cleanedData['wfh'])	
			elif key == 'compoff':
				obj, created = LeaveAccurals.objects.update_or_create(employee=instance, leaveType='COMP', defaults={'accuredLeaves':cleanedData['compoff']})
				#LeaveAccurals.objects.filter(employee=instance).filter(leaveType="COMP").update(accuredLeaves=cleanedData['compoff'])	
			elif key == 'lop':
				obj, created = LeaveAccurals.objects.update_or_create(employee=instance, leaveType='LOP', defaults={'accuredLeaves':cleanedData['lop']})
				#LeaveAccurals.objects.filter(employee=instance).filter(leaveType="LOP").update(accuredLeaves=cleanedData['lop'])	
			else:
				pass
	
		return redirect('employee_details', id=instance.id)

	context = {
		"instance" : instance,
		"empId" : instance.id,
		"empForm" : empForm,
		"lAccForm" : lAccForm,
	}
	return render(request, 'hr/edit_employee.html', context)

def employee_delete(request, id):
	#if not request.user.is_staff or not request.user.is_superuser:
	#	raise Http404
	if not request.user.is_authenticated():
		return redirect('auth_login')
		
	empInfo = EmployeesDirectory.objects.get(pk=id)
	if empInfo.delete():
		return redirect('employees_list')

	context = { 'empInfo' : empInfo }
	return render(request, 'hr/view_employee.html', context)

def leaves_allocate(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')

	lAccForm = singleEmployeeLeaveAccuralForm(request.POST or None)
	csvForm = csvImportLeaveAccuralForm(request.POST, request.FILES or None)
	if csvForm.is_valid():
		for key, file in request.FILES.items():
			if key == 'csvFile':
				path = file.name
				# To permanently save the file in media root
				#dest = open(path, 'w')
				#if file.multiple_chunks:
				#	for c in file.chunks():
				#		dest.write(c)
				#else:
				#	dest.write(file.read())
				#dest.close()
				with open(path) as csvFile:
					reader = csv.reader(csvFile, delimiter=',', quoting=csv.QUOTE_NONE)
					for row in reader:
						if len(row) > 1 and len(row) <= 7:
							emp = EmployeesDirectory.objects.get(employee_id=row[0])
							print(emp)
							obj, created = LeaveAccurals.objects.update_or_create(employee=emp, leaveType='PL', defaults={'accuredLeaves':row[1]})
							if row[2]:
								obj, created = LeaveAccurals.objects.update_or_create(employee=emp, leaveType='CL', defaults={'accuredLeaves':row[2]})
							if row[3]:
								obj, created = LeaveAccurals.objects.update_or_create(employee=emp, leaveType='SL', defaults={'accuredLeaves':row[3]})
							if row[4]:
								obj, created = LeaveAccurals.objects.update_or_create(employee=emp, leaveType='COMP', defaults={'accuredLeaves':row[4]})
							if row[5]:
								obj, created = LeaveAccurals.objects.update_or_create(employee=emp, leaveType='WFH', defaults={'accuredLeaves':row[5]})
							if row[6]:
								obj, created = LeaveAccurals.objects.update_or_create(employee=emp, leaveType='LOP', defaults={'accuredLeaves':row[6]})
				break;
	else:
		csvForm = csvImportLeaveAccuralForm()

	if lAccForm.is_valid():
		cleanedData = lAccForm.cleaned_data
		changedData = lAccForm.changed_data
		#print(changedData[1:len(changedData)])
		#print(changedData)
		emp = EmployeesDirectory.objects.get(id=cleanedData['employee'].id)
		for key in changedData[1:len(changedData)]:
			updateValues = { 'accuredLeaves' : cleanedData[key]}
			if key == 'pl':
				queryKey = "PL"
			elif key == 'cl':
				queryKey = "CL"
			elif key == 'sl':
				queryKey = "SL"
			elif key == 'compoff':
				queryKey = "COMP"
			elif key == 'wfh':
				queryKey = "WFH"
			elif key == 'lop':
				queryKey = "LOP"
			else:
				queryKey = "PL"#Default as PL
			obj, created = LeaveAccurals.objects.update_or_create(employee=emp, leaveType=queryKey, defaults=updateValues)
		return redirect('employee_details', id=emp.id)
	else:
		lAccForm = singleEmployeeLeaveAccuralForm()
		
	context = { 'lAccForm' : lAccForm, 'csvForm':csvForm }
	return render(request, 'hr/leaves_allocate.html', context)

def leaves_list(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')

	leavesList = Leaves.objects.all()
	#empList = EmployeesDirectory.objects.all()
	searchQuery = request.GET.get("searchQueryStr")
	if searchQuery:
		leavesList = leavesList.filter(
			Q(reason__icontains=searchQuery) |
			Q(currentProject__icontains=searchQuery)
			)
	context = { 'leavesList' : leavesList }
	return render(request, 'hr/leaves.html', context)		

def employee_leaves(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	empInfo = EmployeesDirectory.objects.filter(user=request.user)
	if empInfo.count() > 0 :
		leavesList = Leaves.objects.filter(employee_id=empInfo)
	context = { 'leavesList' : leavesList }
	return render(request, 'hr/leaves.html', context)		

def leave_create(request):
	#if not request.user.is_staff or not request.user.is_superuser:
	#	raise Http404
	if not request.user.is_authenticated():
		return redirect('auth_login')

	lForm = leaveForm(request.POST, request.FILES or None)
	if lForm.is_valid():
		#leaveData = lForm.cleaned_data
		instance = lForm.save(commit=False)
		instance.save()
		
		subject = "%s Request from %s" % (instance.leaveType, instance.employee_id)
		mailBody = "<p>Dear %s,<br><br>Leave Request from %s, for %s days between %s and %s under %s category.<br><br>Please Login to Portal to validate the request.<br><br>Thanks,<br>HR Admin - Internal Portal</p>"  % (instance.employee_id.manager, instance.employee_id, instance.numberOfDays, instance.startedDate, instance.endDate, instance.leaveType) 
		
		print('>>>>>>>>>> Trying to send email for new Leave Request:')
		try:
			email = EmailMessage(subject, mailBody, settings.DEFAULT_FROM_EMAIL,
            					[instance.employee_id.manager.email], ['noreply@embedur.com'],
            					cc=['venkateshm@embedur.com', instance.employee_id.email])
			email.content_subtype = "html"
			email.send(fail_silently=False)
			instance.update(status=settings.LEAVE_STATUS_CHOICES)
		except:
			print("Mail Send Failed.!!!!!!")
		return redirect('leave_details', id=instance.id)
	else:
		lForm = leaveForm()

	context = {
		"leaveForm" : lForm
	}
	return render(request, 'hr/leave_request.html', context)

def leave_details(request, id):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	leaveInfo = Leaves.objects.get(pk=id)
	context = { 'leaveInfo' : leaveInfo }
	return render(request, 'hr/leave_details.html', context)

def leave_update(request, id):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	instance = get_object_or_404(Leaves, id=id)
	lForm = leaveForm(request.POST or None, instance=instance)
	if lForm.is_valid():
		instance = lForm.save(commit=False)
		instance.save()

		leaveTypeChoices = dict(settings.LEAVE_TYPE_CHOICES)
		leaveStatusChoices = dict(settings.LEAVE_STATUS_CHOICES)
		print(leaveTypeChoices)
		print(leaveStatusChoices)

		return redirect('leaves_list')
	else:
		lForm = leaveForm(instance=instance)

	context = {
		"instance" : instance,
		"leaveForm" : lForm
	}
	return render(request, 'hr/edit_leave.html', context)
