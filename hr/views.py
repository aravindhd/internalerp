from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.forms import inlineformset_factory, modelformset_factory
from datetime import date, datetime
from decimal import Decimal
from workdays import networkdays
from .models import Country, Organization, Holidays
from .models import EmployeesDirectory, Department, EmploymentHistory, LeaveAccurals, Leaves
from assets.models import Assets
from .forms import countryForm, organizationForm, holidaysForm
from .forms import employeeForm, leaveRequestForm, leaveEditForm, leaveAccuralForm, singleEmployeeLeaveAccuralForm, csvImportLeaveAccuralForm
from .tables import EmployeesTable
from django_tables2 import RequestConfig
import csv
from utils.mails import _process_mail_for_leave_request, _process_mail_for_leave_approved_rejected

# Create your views here.
def country_configure(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	if request.method == "POST":
		ctryForm = countryForm(request.POST)
		if ctryForm.is_valid():
			ctryForm.save()
			return redirect('country_list')
		else:
			print("Add Country Form has errors.....")
	else:
		ctryForm = countryForm()		
	context = { "countryForm" : ctryForm }
	return render(request, 'hr/country_configure.html', context)	

def organization_configure(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	if request.method == "POST":
		orgForm = organizationForm(request.POST)
		if orgForm.is_valid():
			orgForm.save()
			return redirect('org_list')
		else:
			print("Add Organization Form has errors.....")
	else:
		orgForm = organizationForm()
	context = { "organizationForm" : orgForm}
	return render(request, 'hr/organization_configure.html', context)
	#return redirect('employees_list')

def country_list(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	countryList = Country.objects.all()
	context = { "countryList" : countryList }
	return render(request, 'hr/countries.html', context)

def organization_list(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	orgList = Organization.objects.all()
	context = { "orgList" : orgList }
	return render(request, 'hr/organizations.html', context)

@permission_required('hr.view_holidays', raise_exception=True)
def view_holidays(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')

	print(request.user.has_perm('hr.view_holidays'))

	holidaysList = Holidays.objects.all()
	context = { "holidaysList" : holidaysList }
	return render(request, 'hr/holidays.html', context)

def add_holiday(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	if request.method == "POST":
		holidayForm = holidaysForm(request.POST)
		if holidayForm.is_valid():
			holidayForm.save()
			return redirect('view_holidays')
		else:
			print("Add Holiday Form has errors.....")
	else:
		holidayForm = holidaysForm()
	context = { "holidayForm" : holidayForm}
	return render(request, 'hr/addHoliday.html', context)

def employees_table(request):
	#if not request.user.is_staff or not request.user.is_superuser:
	#	raise Http404
	if not request.user.is_authenticated():
		return redirect('auth_login')

	empTable = EmployeesTable(EmployeesDirectory.objects.all())
	RequestConfig(request, paginate={ "per_page" : 10 }).configure(empTable)
	context = { 'empList' : empTable }
	return render(request, 'hr/employees_table.html', context)

@permission_required('hr.view_employeesdirectory', raise_exception=True)
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
	except EmptyPage:
		empList = paginator.page(paginator.num_pages)
	context = { 'empList' : empList } #, 'managersList' : managersList }
	return render(request, 'hr/employees.html', context)

@permission_required('hr.view_employeesdirectory', raise_exception=True)
def employees_list_per_manager(request):
	#if not request.user.is_staff or not request.user.is_superuser:
	#	raise Http404

	if not request.user.is_authenticated():
		return redirect('auth_login')

	mgr = EmployeesDirectory.objects.filter(user=request.user)
	if mgr.count() > 0 :
		empList = EmployeesDirectory.objects.filter(manager=mgr)
	
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

@permission_required('hr.view_employeesdirectory', raise_exception=True)
@permission_required('hr.view_leaveaccurals', raise_exception=True)
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

	assetsList = Assets.objects.filter(Q(status__icontains = 'ASSIGNED') & 
										(Q(assignmentCategory__icontains = 'EMPLOYEE') |
										  Q(assignmentCategory__icontains = 'SHARED'))& 
										Q(assignedTo__firstname__icontains=empInfo.firstname))

	context = { 'empInfo' : empInfo, 'leaveAccuralList' : leaveAccuralList, "assetsList" : assetsList }
	return render(request, 'hr/view_employee.html', context)

@permission_required('hr.add_employeesdirectory', raise_exception=True)
def employee_create(request):
	#if not request.user.is_staff or not request.user.is_superuser:
	#	raise Http404
	if not request.user.is_authenticated():
		return redirect('auth_login')
	if request.method == "POST":
		empForm = employeeForm(request.POST, request.FILES or None)
		lAccForm = leaveAccuralForm(request.POST or None)
		if empForm.is_valid() and lAccForm.is_valid():
			empData = empForm.cleaned_data
			
			## Create a user account first with given email alias else firstname & lastname 
			## then proceed for creating Employee details
			username = '%s' % (empData['email'].split('@')[0])
			if len(username) <= 0 :
				print("Email Alias not available so creating based on firstname, lastname....")
				username = '%s%s' %(empData['firstname'], empData['lastname'][0])
			user = User.objects.create_user(username.lower(), empData['email'], settings.DEFAULT_USER_ACCOUNT_PASSWD)
			user.first_name=empData['firstname']
			user.last_name=empData['lastname']
			empGroup, created = Group.objects.get_or_create(name=empData['role'], defaults={ 'name' : empData['role'] })
			user.groups.add(empGroup)
			assetGroup, created = Group.objects.get_or_create(name=empData['assets_privilege'], defaults={ 'name' : empData['assets_privilege'] })
			user.groups.add(assetGroup)
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
		else:	# Form has errors
			print("Invalid New Employee FORM......")
	else:
		empForm = employeeForm()
		lAccInitData = { 'pl' : 0.00, 'cl' : 0.00, 'sl' : 0.00, 'lop' : 0.00, 'wfh' : 0.00, 'compoff' : 0.00}
		lAccForm = leaveAccuralForm(initial=lAccInitData)

	context = {
		"empForm" : empForm,
		"lAccForm" : lAccForm
	}
	return render(request, 'hr/new_employee.html', context)

@permission_required('hr.change_employeesdirectory', raise_exception=True)
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

@permission_required('hr.delete_employeesdirectory', raise_exception=True)
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

@permission_required('hr.add_leaveaccurals', raise_exception=True)
def leaves_allocate(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	if request.method == "POST":
		
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
			print("Leave Allocate CSV Form has errors......")

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
			print("Leave Allocate singleEmployeeLeaveAccuralForm has errors......")
	else:
		csvForm = csvImportLeaveAccuralForm()
		lAccForm = singleEmployeeLeaveAccuralForm()
		
	context = { 'lAccForm' : lAccForm, 'csvForm':csvForm }
	return render(request, 'hr/leaves_allocate.html', context)

@permission_required('hr.view_leaves', raise_exception=True)
def leaves_list(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')

	leavesList = Leaves.objects.all().order_by(F('id').desc())
	#empList = EmployeesDirectory.objects.all()
	searchQuery = request.GET.get("searchQueryStr")
	if searchQuery:
		leavesList = leavesList.filter(
			Q(reason__icontains=searchQuery)
			| Q(currentProject__icontains=searchQuery)
			| Q(employee_id__firstname__icontains=searchQuery)
			#| Q(employee_id__lastname__icontains=searchQuery)
			| Q(leaveType__icontains=searchQuery)
			| Q(status__icontains=searchQuery)
			)
	startDateSearch = request.GET.get("searchQueryStartDate")
        endDateSearch = request.GET.get("searchQueryEndDate")
	if startDateSearch and endDateSearch:
		#print("Start Date based search received!!!!!!......")
		leavesList = leavesList.filter(
			Q(startedDate__range=(startDateSearch, endDateSearch)) |
                        Q(endDate__range=(startDateSearch, endDateSearch))
			)
	elif startDateSearch:
		#print("Start Date based search received!!!!!!......")
		leavesList = leavesList.filter(
			Q(startedDate__lte=startDateSearch) & Q(endDate__gte=startDateSearch)
			)
	elif endDateSearch:
		#print("End Date based search received!!!!!!......")
		leavesList = leavesList.filter(
			#Q(endDate__exact=endDateSearch)
                        Q(startedDate__lte=endDateSearch) &
                        Q(endDate__gte=endDateSearch)
			)
	paginator = Paginator(leavesList, settings.DEFAULT_PAGINATOR_RECORDS_PERPAGE)
	page = request.GET.get("page")
	try:
		leavesList = paginator.page(page)
	except PageNotAnInteger:
		leavesList = paginator.page(1)
	context = { 'leavesList' : leavesList }
	return render(request, 'hr/leaves.html', context)		

@permission_required('hr.view_leaves', raise_exception=True)
def leaves_list_per_manager(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')

	mgr = EmployeesDirectory.objects.filter(user=request.user)
	leavesList = Leaves.objects.filter(employee_id__manager=mgr).order_by(F('id').desc())
	#empList = EmployeesDirectory.objects.all()
        searchQuery = request.GET.get("searchQueryStr")
        if searchQuery:
                leavesList = leavesList.filter(
                        Q(reason__icontains=searchQuery)
                        | Q(currentProject__icontains=searchQuery)
                        | Q(employee_id__firstname__icontains=searchQuery)
                        #| Q(employee_id__lastname__icontains=searchQuery)
                        | Q(leaveType__icontains=searchQuery)
                        | Q(status__icontains=searchQuery)
                        )
        startDateSearch = request.GET.get("searchQueryStartDate")
        endDateSearch = request.GET.get("searchQueryEndDate")
        if startDateSearch and endDateSearch:
                #print("Start Date based search received!!!!!!......")
                leavesList = leavesList.filter(
                        Q(startedDate__range=(startDateSearch, endDateSearch)) |
                        Q(endDate__range=(startDateSearch, endDateSearch))
                        )
        elif startDateSearch:
                #print("Start Date based search received!!!!!!......")
                leavesList = leavesList.filter(
                        Q(startedDate__lte=startDateSearch) &
                        Q(endDate__gte=startDateSearch)
                        )
        elif endDateSearch:
                #print("End Date based search received!!!!!!......")
                leavesList = leavesList.filter(
                        #Q(endDate__exact=endDateSearch)
                        Q(startedDate__lte=endDateSearch) &
                        Q(endDate__gte=endDateSearch)
                        )
	paginator = Paginator(leavesList, settings.DEFAULT_PAGINATOR_RECORDS_PERPAGE)
	page = request.GET.get("page")
	try:
		leavesList = paginator.page(page)
	except PageNotAnInteger:
		leavesList = paginator.page(1)
	context = { 'leavesList' : leavesList }
	return render(request, 'hr/leaves.html', context)


@permission_required('hr.view_leaves', raise_exception=True)
def leaves_to_approve(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')

	leavesList = Leaves.objects.filter(Q(status='SUBMITTED') | Q(status='REOPENED')).order_by(F('id').desc())
	searchQuery = request.GET.get("searchQueryStr")
	if searchQuery:
		leavesList = leavesList.filter(
			Q(reason__icontains=searchQuery)
			| Q(currentProject__icontains=searchQuery)
			| Q(employee_id__firstname__icontains=searchQuery)
			#| Q(employee_id__lastname__icontains=searchQuery)
			| Q(leaveType__icontains=searchQuery)
			| Q(status__icontains=searchQuery)
			)
	startDateSearch = request.GET.get("searchQueryStartDate")
	if startDateSearch:
		#print("Start Date based search received!!!!!!......")
		leavesList = leavesList.filter(
			#Q(startedDate__icontains=startDateSearch)
			Q(startedDate__gte=startDateSearch)
			)
	endDateSearch = request.GET.get("searchQueryEndDate")
	if endDateSearch:
		#print("End Date based search received!!!!!!......")
		leavesList = leavesList.filter(
			#Q(endDate__icontains=endDateSearch)
			Q(endDate__lte=endDateSearch)
			)
	paginator = Paginator(leavesList, settings.DEFAULT_PAGINATOR_RECORDS_PERPAGE)
	page = request.GET.get("page")
	try:
		leavesList = paginator.page(page)
	except PageNotAnInteger:
		leavesList = paginator.page(1)
	context = { 'leavesList' : leavesList }
	return render(request, 'hr/leaves.html', context)		

@permission_required('hr.view_leaves', raise_exception=True)
def leaves_to_approve_per_manager(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')

	mgr = EmployeesDirectory.objects.filter(user=request.user)
	leavesList = Leaves.objects.filter(employee_id__manager=mgr).filter(Q(status='SUBMITTED') | Q(status='REOPENED')).order_by(F('id').desc())
	searchQuery = request.GET.get("searchQueryStr")
	if searchQuery:
		leavesList = leavesList.filter(
			Q(reason__icontains=searchQuery)
			| Q(currentProject__icontains=searchQuery)
			| Q(employee_id__firstname__icontains=searchQuery)
			#| Q(employee_id__lastname__icontains=searchQuery)
			| Q(leaveType__icontains=searchQuery)
			| Q(status__icontains=searchQuery)
			)
	startDateSearch = request.GET.get("searchQueryStartDate")
	if startDateSearch:
		#print("Start Date based search received!!!!!!......")
		leavesList = leavesList.filter(
			#Q(startedDate__icontains=startDateSearch)
			Q(startedDate__gte=startDateSearch)
			)
	endDateSearch = request.GET.get("searchQueryEndDate")
	if endDateSearch:
		#print("End Date based search received!!!!!!......")
		leavesList = leavesList.filter(
			#Q(endDate__icontains=endDateSearch)
			Q(endDate__lte=endDateSearch)
			)
	paginator = Paginator(leavesList, settings.DEFAULT_PAGINATOR_RECORDS_PERPAGE)
	page = request.GET.get("page")
	try:
		leavesList = paginator.page(page)
	except PageNotAnInteger:
		leavesList = paginator.page(1)
	context = { 'leavesList' : leavesList }
	return render(request, 'hr/leaves.html', context)


#@permission_required('hr.view_leaves', raise_exception=True)
def leave_details(request, id):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	leaveInfo = Leaves.objects.get(pk=id)
	context = { 'leaveInfo' : leaveInfo }
	return render(request, 'hr/leave_details.html', context)

#@permission_required('hr.view_leaves', raise_exception=True)
def employee_leaves(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	empInfo = EmployeesDirectory.objects.filter(user=request.user)
	if empInfo.count() > 0 :
		leavesList = Leaves.objects.filter(employee_id=empInfo).order_by(F('id').desc())
	context = { 'leavesList' : leavesList }
	return render(request, 'hr/leaves.html', context)		

@permission_required('hr.add_leaves', raise_exception=True)
def leave_create(request):
	#if not request.user.is_staff or not request.user.is_superuser:
	#	raise Http404
	if not request.user.is_authenticated():
		return redirect('auth_login')
	emp = EmployeesDirectory.objects.get(user=request.user)
	holidaysList = Holidays.objects.filter(country=emp.organization.country)

	if request.method == "POST":
		if emp.role == 'HR-MANAGER':	# TODO: Instaed of manager check user role in future
			lForm = leaveRequestForm(False, request.POST, request.FILES or None, initial = {'employee_id': emp })	
		else:
			lForm = leaveRequestForm(True, request.POST, request.FILES or None, initial = {'employee_id': emp })

		if lForm.is_valid():
			#leaveData = lForm.cleaned_data
			instance = lForm.save(commit=False)
			
			# Send EMAIL
			_process_mail_for_leave_request(instance, 'html')
			
			print("Updating the Status after mail sent")
			instance.status = "SUBMITTED"
			instance.save()

			return redirect('leave_details', id=instance.id)
	else:
		# TODO: Instaed of manager check user role in future
		if emp.role == 'HR-MANAGER':
			lForm = leaveRequestForm(False, initial = {'employee_id': emp })
		else:
			lForm = leaveRequestForm(True, initial = {'employee_id': emp })

	context = {
		"leaveForm" : lForm,
		"holidaysList" : holidaysList
	}
	return render(request, 'hr/leave_request.html', context)

@permission_required('hr.change_leaves', raise_exception=False)
def leave_update(request, id):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	instance = get_object_or_404(Leaves, id=id)
	print("Getting the Manager details")
	print(instance.employee_id.manager)
	
	leaveStatusChoices = dict(settings.LEAVE_STATUS_CHOICES)
	print(leaveStatusChoices)
	contextLeaveStatusChoices = []
	userRole = 'employee'
	if instance.employee_id.manager and (request.user == instance.employee_id.manager.user):
		# Manager Login
		print("Manager corresponding to this leave records UPDATES it.")
		contextLeaveStatusChoices.append(('APPROVED', 'Approve'),)
		contextLeaveStatusChoices.append(('REJECTED', 'Reject'),)
		userRole = 'manager'
	elif instance.employee_id.user == request.user:
		# Employee login
		print("Employee corresponding to this leave records UPDATES it.")
		if instance.status == "SUBMITTED":
			contextLeaveStatusChoices.append(('SUBMITTED', 'Submit'),)
		contextLeaveStatusChoices.append(('REOPENED', 'Re-Open'),)
		contextLeaveStatusChoices.append(('DISCARD', 'Discard'),)
		userRole = 'employee'
	else:
		# Admin Login
		contextLeaveStatusChoices = settings.LEAVE_STATUS_CHOICES
		print("Admin updating the leave record")
		userRole = 'admin'

	if request.method == "POST":
		lForm = leaveEditForm(contextLeaveStatusChoices, userRole, request.POST or None, instance=instance)
	
		#print("Trying to verify whether leaveEditForm is valid or not!!!!!")
		if lForm.is_valid():
			#print("Form validated.....")
			cleanedData = lForm.cleaned_data
			instance = lForm.save(commit=False)		# Has Custom FORM save definition
			
			# Send EMAIL
			if instance.status == 'APPROVED' or instance.status == 'REJECTED':
				_process_mail_for_leave_approved_rejected(instance, 'html')

			if userRole == 'manager':
				return redirect('leaves_to_approve_per_manager')
			elif userRole == 'admin':
				return redirect('leaves_list')
			else:
				return redirect('employee_leaves')
	else:
		print(">>>>> GET Leave Update:....")
		lForm = leaveEditForm(contextLeaveStatusChoices, userRole, instance=instance)
		print(lForm.fields['status'])
		#lForm.fields['employee_id'].widget.attrs['readonly'] = True # text input
		#lForm.fields['employee_id'].widget.attrs['disabled'] = True # text input

	context = {
		"instance" : instance,
		"leaveForm" : lForm
	}
	return render(request, 'hr/edit_leave.html', context)

@permission_required(['hr.view_leaveaccurals', 'hr.view_leaves', 'hr.view_employeesdirectory', 'hr.view_holidays'], raise_exception=True)
def hr_data_export(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')

	if request.method == "GET":
		exportCategory = request.GET.get("exportCategory")
		if exportCategory:
			# Create the HttpResponse object with the appropriate CSV header.
			response = HttpResponse(content_type='text/csv')

			searchStr = request.GET.get("searchStr")
			sortby = request.GET.get("sortby")
			employeeSelect = request.GET.get("employeeSelect")

			if exportCategory == 'employees':
				response['Content-Disposition'] = 'attachment; filename="employeesDirectory.csv"'
				writer = csv.writer(response)
				if (employeeSelect != '--'):
					emp = get_object_or_404(EmployeesDirectory, id=employeeSelect)
					writer.writerow(['ID', 'Firstname', 'Lastname', 'Employee_ID', 'Email', 'Manager', 'Designation'])
					writer.writerow([emp.id, emp.firstname, emp.lastname, emp.employee_id, emp.email, emp.manager, emp.designation])
				else:
					if sortby != '--':
						employeesList = EmployeesDirectory.objects.all().order_by(sortby)
					else:
						employeesList = EmployeesDirectory.objects.all()

					if searchStr:
						employeesList = employeesList.filter(
							Q(designation__icontains=searchStr) |
							Q(manager__firstname__icontains=searchStr) |
							Q(manager__lastname__icontains=searchStr)
							)
					writer.writerow(['ID', 'Firstname', 'Lastname', 'Employee_ID', 'Email', 'Manager', 'Designation'])
					for emp in employeesList:
						writer.writerow([emp.id, emp.firstname, emp.lastname, emp.employee_id, emp.email, emp.manager, emp.designation])
					pass
			elif exportCategory == 'leaves':
				response['Content-Disposition'] = 'attachment; filename="employeesLeaveHistory.csv"'
				writer = csv.writer(response)
				writer.writerow(['ID','Employee', 'Leave Summary', 'Leave Type', 'Start Date', 'End Date', '# Days', 'Status'])

				if (employeeSelect != '--'):
					emp = get_object_or_404(EmployeesDirectory, id=employeeSelect)
					leavesList = Leaves.objects.filter(employee_id=emp).order_by(F('id').asc())
					# filter(Q(status='SUBMITTED') | Q(status='REOPENED')).order_by
					# Dump the collected leave history into CSV
					for leave in leavesList:
						writer.writerow([leave.id, leave.employee_id, leave.reason, leave.leaveType, leave.startedDate, leave.endDate, leave.numberOfDays, leave.status])
				else:
					leaveType = request.GET.get("leaveType")
					startDateSearch = request.GET.get("startDate")
					endDateSearch = request.GET.get("endDate")

					if sortby != '--':
						employeesList = EmployeesDirectory.objects.all().order_by(sortby)
					else:
						employeesList = EmployeesDirectory.objects.all()

					if searchStr:
						employeesList = employeesList.filter(
							Q(designation__icontains=searchStr) |
							Q(manager__firstname__icontains=searchStr) |
							Q(manager__lastname__icontains=searchStr)
							)
					for emp in employeesList:
						leavesList = Leaves.objects.filter(employee_id=emp).order_by(F('id').asc())
						if leaveType != '--':
							leavesList = leavesList.filter(Q(leaveType__icontains=leaveType))

						if startDateSearch and endDateSearch:
							leavesList = leavesList.filter(
								Q(startedDate__range=(startDateSearch, endDateSearch)) |
					            Q(endDate__range=(startDateSearch, endDateSearch))
								)
						elif startDateSearch:
							leavesList = leavesList.filter(
								Q(startedDate__lte=startDateSearch) &
								Q(endDate__gte=startDateSearch)
								)
						elif endDateSearch:
							leavesList = leavesList.filter(
								#Q(endDate__exact=endDateSearch)
		                        Q(startedDate__lte=endDateSearch) &
		                        Q(endDate__gte=endDateSearch)
								)
						# Dump the collected leave history into CSV
						for leave in leavesList:
							writer.writerow([leave.id, leave.employee_id, leave.reason,  leave.leaveType, leave.startedDate, leave.endDate, leave.numberOfDays, leave.status])
						#employeesList for-loop ends here
				pass
			elif exportCategory == 'leavebalances':
				response['Content-Disposition'] = 'attachment; filename="employeesLeaveAccruals.csv"'
				writer = csv.writer(response)
				writer.writerow(['Employee', 'CL', 'PL', 'SL', 'COMP-OFF', 'LOP', 'WFH'])

				isPayroll = request.GET.get("isPayroll")
				payrollDateSearch = request.GET.get("payrollDate")

				if (employeeSelect != '--'):
					emp = get_object_or_404(EmployeesDirectory, id=employeeSelect)
					if isPayroll:
						if payrollDateSearch:
							lAccrual = payrollLeaveAccrualPerEmployee(emp, payrollDateSearch)
						else:
							lAccrual = payrollLeaveAccrualPerEmployee(emp, date.today())
						#print("*** [PAYROLL] Leave Balance for Employee  [%s]  ***********" % (emp))
						#print("CL-%s, PL-%s, SL-%s, COMP-%s, LOP-%s, WFH-%s.." %(lAccrual['CL'], lAccrual['PL'], lAccrual['SL'], lAccrual['COMP'], lAccrual['LOP'], lAccrual['WFH']))
						writer.writerow(['%s'% (emp), '%s' %(lAccrual['CL']), '%s'%(lAccrual['PL']), '%s'%(lAccrual['SL']), '%s'%(lAccrual['COMP']), '%s'%(lAccrual['LOP']), '%s'%(lAccrual['WFH'])])
					else:
						cl = 0.0
						pl = 0.0
						sl = 0.0
						comp = 0.0
						wfh = 0.0
						lop =0.0
						lAccList = LeaveAccurals.objects.filter(employee=emp)
						for lAcc in lAccList:
							if lAcc.leaveType == 'CL':
								cl = lAcc.accuredLeaves
							elif lAcc.leaveType == 'PL':
								pl = lAcc.accuredLeaves
							elif lAcc.leaveType == 'SL':
								sl = lAcc.accuredLeaves
							elif lAcc.leaveType == 'COMP':
								comp = lAcc.accuredLeaves
							elif lAcc.leaveType == 'LOP':
								lop = lAcc.accuredLeaves
							elif lAcc.leaveType == 'WFH':
								wfh = lAcc.accuredLeaves
						#print("Leave Balance for Employee >> %s : CL-%s, PL-%s, SL-%s, COMP-%s, LOP-%s, WFH-%s.." % (emp, cl, pl, sl, comp, lop, wfh))
						writer.writerow(['%s'% (emp), '%s' %(cl), '%s'%(pl), '%s'%(sl), '%s'%(comp), '%s'%(lop), '%s'%(wfh)])
				else:
					if sortby != '--':
						employeesList = EmployeesDirectory.objects.all().order_by(sortby)
					else:
						employeesList = EmployeesDirectory.objects.all()

					if searchStr:
						employeesList = employeesList.filter(
							Q(designation__icontains=searchStr) |
							Q(manager__firstname__icontains=searchStr) |
							Q(manager__lastname__icontains=searchStr)
							)
					for emp in employeesList:
						if isPayroll:
							if payrollDateSearch:
								lAccrual = payrollLeaveAccrualPerEmployee(emp, payrollDateSearch)
							else:
								lAccrual = payrollLeaveAccrualPerEmployee(emp, date.today())
							#print("[PAYROLL] Leave Balance for Employee  [%s] >>>" % (emp))
							#print("CL-%s, PL-%s, SL-%s, COMP-%s, LOP-%s, WFH-%s.." %(lAccrual['CL'], lAccrual['PL'], lAccrual['SL'], lAccrual['COMP'], lAccrual['LOP'], lAccrual['WFH']))
							writer.writerow(['%s'% (emp), '%s' %(lAccrual['CL']), '%s'%(lAccrual['PL']), '%s'%(lAccrual['SL']), '%s'%(lAccrual['COMP']), '%s'%(lAccrual['LOP']), '%s'%(lAccrual['WFH'])])
						else:
							cl = 0.0
							pl = 0.0
							sl = 0.0
							comp = 0.0
							wfh = 0.0
							lop =0.0
							lAccList = LeaveAccurals.objects.filter(employee=emp)
							for lAcc in lAccList:
								if lAcc.leaveType == 'CL':
									cl = lAcc.accuredLeaves
								elif lAcc.leaveType == 'PL':
									pl = lAcc.accuredLeaves
								elif lAcc.leaveType == 'SL':
									sl = lAcc.accuredLeaves
								elif lAcc.leaveType == 'COMP':
									comp = lAcc.accuredLeaves
								elif lAcc.leaveType == 'LOP':
									lop = lAcc.accuredLeaves
								elif lAcc.leaveType == 'WFH':
									wfh = lAcc.accuredLeaves
							#print("%s : CL-%s, PL-%s, SL-%s, COMP-%s, LOP-%s, WFH-%s.." % (emp, cl, pl, sl, comp, lop, wfh))
							writer.writerow(['%s'% (emp), '%s' %(cl), '%s'%(pl), '%s'%(sl), '%s'%(comp), '%s'%(lop), '%s'%(wfh)])
					# employeesList FOR Loop ends here
				pass
			return response
		else:
			employeesList = EmployeesDirectory.objects.all()
		pass

	context = { "employeesList" : employeesList }
	return render(request, 'hr/data_export.html', context)

def payrollLeaveAccrualPerEmployee(employeeObj, payrollDateSearch):
	lAccrual = {}
	cl = 0.0
	pl = 0.0
	sl = 0.0
	comp = 0.0
	wfh = 0.0
	lop =0.0
	lastDay = date(date.today().year, 12, 31)
	#print("Last Day of Year : %s, Payroll Date : %s.." % (lastDay, payrollDateSearch))

	lAccList = LeaveAccurals.objects.filter(employee=employeeObj)
	leavesList = Leaves.objects.order_by('leaveType').filter(
								Q(employee_id__exact=employeeObj) & 
								(
									Q(status__exact='APPROVED') |
									Q(status__exact='SUBMITTED') |
									Q(status__exact='REOPENED')
								) &
								(
									Q(startedDate__range=(payrollDateSearch, lastDay)) |
									Q(endDate__range=(payrollDateSearch, lastDay))
								)
							)
 
	if not lAccrual.has_key('CL'):
		lAccrual['CL'] = 0.0
	if not lAccrual.has_key('PL'):
		lAccrual['PL'] = 0.0
	if not lAccrual.has_key('SL'):
		lAccrual['SL'] = 0.0
	if not lAccrual.has_key('COMP'):
		lAccrual['COMP'] = 0.0
	if not lAccrual.has_key('LOP'):
		lAccrual['LOP'] = 0.0
	if not lAccrual.has_key('WFH'):
		lAccrual['WFH'] = 0.0
	
	for lAcc in lAccList:
		lAccrual['%s'%(lAcc.leaveType)] = lAcc.accuredLeaves

	for leave in leavesList:
		numDays = leave.numberOfDays

		temp = datetime.strptime(payrollDateSearch, '%Y-%m-%d')
		payrollDate = date(temp.year, temp.month, temp.day)
		fromDate = leave.startedDate
		endDate = leave.endDate
		#print("From : %s, Payroll : %s, End : %s.." % (fromDate, payrollDate, endDate))

		if (fromDate <= payrollDate) and (endDate >= payrollDate):
			#print("-------- OVERLAPPING LEAVE WITH PAYROLL DATE")
			holidays = Holidays.objects.filter(country=employeeObj.organization.country).values('date')
			empHolidays = []
			for holiday in holidays:
				empHolidays.append(holiday['date'])
			numDays = Decimal(networkdays(fromDate, payrollDate, empHolidays))
			#print("Actual Number of Past Leave Days: [%s]" % (Decimal(numberBusinessDays)))

		if leave.leaveType == 'CL':
			if lAccrual.has_key('CL'):
				lAccrual['CL'] = (lAccrual['CL'] + numDays)
			else:
				lAccrual['CL'] = numDays
		elif leave.leaveType == 'PL':
			if lAccrual.has_key('PL'):
				lAccrual['PL'] = (lAccrual['PL'] + numDays)
			else:
				lAccrual['PL'] = numDays
		elif leave.leaveType == 'SL':
			if lAccrual.has_key('SL'):
				lAccrual['SL'] = (lAccrual['SL'] + numDays)
			else:
				lAccrual['SL'] = numDays
		elif leave.leaveType == 'COMP':
			if lAccrual.has_key('COMP'):
				lAccrual['COMP'] = (lAccrual['COMP'] + numDays)
			else:
				lAccrual['COMP'] = numDays
		elif leave.leaveType == 'LOP':
			if lAccrual.has_key('LOP'):
				lAccrual['LOP'] = (lAccrual['LOP'] + numDays)
			else:
				lAccrual['LOP'] = numDays
		elif leave.leaveType == 'WFH':
			if lAccrual.has_key('WFH'):
				lAccrual['WFH'] = (lAccrual['WFH'] + numDays)
			else:
				lAccrual['WFH'] = numDays

	return lAccrual