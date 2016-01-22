from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.db.models import Q
from django.forms import inlineformset_factory, modelformset_factory
from .models import EmployeesDirectory, Department, EmploymentHistory, LeaveAccurals, Leaves
from .forms import employeeForm, leaveForm
from .tables import EmployeesTable
from django_tables2 import RequestConfig

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

	empList_all = EmployeesDirectory.objects.all()
	
	searchQuery = request.GET.get("searchQueryStr")
	if searchQuery:
		empList_all = empList_all.filter(
			Q(firstname__icontains=searchQuery) |
			Q(lastname__icontains=searchQuery) |
			Q(designation__icontains=searchQuery) |
			Q(employee_id__icontains=searchQuery) |
			Q(email__icontains=searchQuery)
			#Q(user__last_name__icontains=searchQuery)
			)
	else:
		print("Search query not received")
	'''
	paginator = Paginator(empList_all, 25)
	page = request.GET.get("page")
	try:
		empList = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		empList = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        empList = paginator.page(paginator.num_pages)
    '''
	context = { 'empList' : empList_all } #, 'managersList' : managersList }
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
	print (">>>>>>>>>>>>>>>>")
	print (leaveAccuralList)
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
	if empForm.is_valid():
		instance = empForm.save(commit=False)
		instance.save()
		return redirect('employee_details', id=instance.id)
	else:
		empForm = employeeForm()

	context = {
		"empForm" : empForm
	}
	return render(request, 'hr/new_employee.html', context)

def employee_update(request, id):
	#if not request.user.is_staff or not request.user.is_superuser:
	#	raise Http404
	if not request.user.is_authenticated():
		return redirect('auth_login')
		
	instance = get_object_or_404(EmployeesDirectory, id=id)
	empForm = employeeForm(request.POST or None, request.FILES or None, instance=instance)
	if empForm.is_valid():
		instance = empForm.save(commit=False)
		instance.save()
		return redirect('employee_details', id=instance.id)

	context = {
		"instance" : instance,
		"empId" : instance.id,
		"empForm" : empForm
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

## Need to update this function
def leaves_allocate(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')

	LeaveAccuralsFormSet = modelformset_factory(LeaveAccurals, fields=('employee', 'leaveType', 'accuredLeaves'))
	
	#empLeaveAccuralsFormSet = inlineformset_factory(EmployeesDirectory, LeaveAccurals, fields=('employee', 'leaveType', 'accuredLeaves'))
	#emp = EmployeesDirectory.objects.filter(user=request.user)
	#empLeaveAccuralsFormSet(instance=emp)

	if request.method == "POST":
		lAccFormset = LeaveAccuralsFormSet(request.POST)
		if lAccFormset.is_valid():
			lAccFormset.save()
			#instances = lAccFormset.save(commit=False)
			#for instance in instances:
		    #	instance.save()
	else:
		lAccFormset = LeaveAccuralsFormSet() 
		#lAccFormset =LeaveAccuralsFormSet(queryset=LeaveAccurals.objects.filter(leaveType__startswith='PL'))

	context = { 'formset' : lAccFormset }
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
		instance = lForm.save(commit=False)
		instance.save()
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
		return redirect('leaves_list')
	else:
		lForm = leaveForm(instance=instance)

	context = {
		"instance" : instance,
		"leaveForm" : lForm
	}
	return render(request, 'hr/edit_leave.html', context)
