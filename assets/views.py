from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from .models import AssetCategories, Assets
from hr.models import EmployeesDirectory
from .forms import assetCategoryForm, assetForm, availAssetForm
from tagging.models import TaggedItem

# Create your views here.
def asset_category_add(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	if request.method == "POST":
		categoryForm = assetCategoryForm(request.POST)
		if categoryForm.is_valid():
			categoryForm.save()
			return redirect('asset_categories')
		else:
			print("Add Asset Category Form has errors.....")
	else:
		categoryForm = assetCategoryForm()		
	context = { "categoryForm" : categoryForm }
	return render(request, 'assets/category_add.html', context)	

def asset_categories(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	categories = AssetCategories.objects.all()
	context = { "categories" : categories }
	return render(request, 'assets/categories.html', context)

def get_assets_by_category(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')

	
	if request.is_ajax() and request.method == 'POST':
		category = request.POST.get("category")
		if category:
			assetsList = Assets.objects.filter(category=category)
			pass
		else:
			assetsList = Assets.objects.all()
			pass
	else:
		assetsList = Assets.objects.all()

	return render(request,'assets/ajax_get_assets.html', locals())

def asset_add(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	if request.method == "POST":
		aForm = assetForm(request.POST)
		if aForm.is_valid():
			#leaveData = lForm.cleaned_data
			instance = aForm.save(commit=False)

			# Send EMAIL
			#_process_mail_for_leave_request(instance, 'html')

			instance.save()
			return redirect('assets_view')
		else:
			print("Error in assetForm() Form")
		pass
	else:
		aForm = assetForm()
		pass
	context = {
		"aForm" : aForm
	}
	return render(request, 'assets/asset_form.html', context)

def assets_view(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	searchQuery = request.GET.get("searchQueryStr")
	searchByTags = request.GET.get("searchByTags")
	assetsList = Assets.objects.all()
	if searchQuery:
		assetsList = assetsList.filter(
			Q(name__icontains=searchQuery) |
			Q(status__icontains=searchQuery) |
			Q(assetId__icontains=searchQuery) |
			Q(model__icontains=searchQuery) |
			Q(assignmentCategory__icontains=searchQuery) |
			Q(assignedTo__firstname__icontains=searchQuery)
			)
		pass
	if searchByTags:
		assetsList = TaggedItem.objects.get_by_model(assetsList, searchByTags)
	context = { "assetsList" : assetsList }
	return render(request, 'assets/assets_view.html', context)

def assets_assigned(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	searchQuery = request.GET.get("searchQueryStr")
	searchByTags = request.GET.get("searchByTags")
	assetsList = Assets.objects.filter(status='ASSIGNED')
	if searchQuery:
		assetsList = assetsList.filter(
			Q(name__icontains=searchQuery) |
			Q(assetId__icontains=searchQuery) |
			Q(model__icontains=searchQuery) |
			Q(assignmentCategory__icontains=searchQuery) |
			Q(assignedTo__firstname__icontains=searchQuery)
			)
		pass
	if searchByTags:
		assetsList = TaggedItem.objects.get_by_model(assetsList, searchByTags)
	context = { "assetsList" : assetsList }
	return render(request, 'assets/assets_view.html', context)

def assets_instock(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	searchQuery = request.GET.get("searchQueryStr")
	searchByTags = request.GET.get("searchByTags")
	assetsList = Assets.objects.filter(status='INSTOCK')
	if searchQuery:
		assetsList = assetsList.filter(
			Q(name__icontains=searchQuery) |
			Q(assetId__icontains=searchQuery) |
			Q(model__icontains=searchQuery) |
			Q(assignmentCategory__icontains=searchQuery) |
			Q(assignedTo__firstname__icontains=searchQuery)
			)
		pass
	if searchByTags:
		assetsList = TaggedItem.objects.get_by_model(assetsList, searchByTags)
	context = { "assetsList" : assetsList }
	return render(request, 'assets/assets_view.html', context)

def asset_details(request, id):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	assetInfo = get_object_or_404(Assets, id=id)
	context = { 'assetInfo' : assetInfo }
	return render(request, 'assets/asset_details.html', context)

def assets_per_employee(request, id):
	if not request.user.is_authenticated():
		return redirect('auth_login')

	empInfo = get_object_or_404(EmployeesDirectory, id=id)
	assetsList = Assets.objects.filter(Q(status__icontains = 'ASSIGNED') & 
										(Q(assignmentCategory__icontains = 'EMPLOYEE') |
										  Q(assignmentCategory__icontains = 'SHARED'))& 
										Q(assignedTo__firstname__icontains=empInfo.firstname))
	context = { "assetsList" : assetsList }
	return render(request, 'assets/assets_view.html', context)

def myassets(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')

	empInfo = get_object_or_404(EmployeesDirectory, user=request.user)
	assetsList = Assets.objects.filter(Q(status__icontains = 'ASSIGNED') & 
										(Q(assignmentCategory__icontains = 'EMPLOYEE') |
										  Q(assignmentCategory__icontains = 'SHARED'))& 
										Q(assignedTo__firstname__icontains=empInfo.firstname))
	context = { "assetsList" : assetsList }
	return render(request, 'assets/assets_view.html', context)

def asset_update(request, id):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	instance = get_object_or_404(Assets, id=id)
	if request.method == "POST":
		aForm = assetForm(request.POST or None, request.FILES or None, instance=instance)
		if aForm.is_valid():
			#leaveData = lForm.cleaned_data
			instance = aForm.save(commit=False)

			# Send EMAIL
			#_process_mail_for_leave_request(instance, 'html')

			instance.save()
			return redirect('asset_details', id=instance.id)
		else:
			print("Error in assetForm() Form")
		pass
	else:
		aForm = assetForm(instance=instance)
		pass
	context = { 'aForm' : aForm }
	return render(request, 'assets/asset_form.html', context)

def asset_avail(request):
	if not request.user.is_authenticated():
		return redirect('auth_login')
	
	if request.method == "POST":
		availForm = availAssetForm(request.POST or None)
		if availForm.is_valid():
			availForm.save()
	else:
		availForm = availAssetForm()
	context = { 'availForm' : availForm }
	return render(request, 'assets/asset_avail.html', context)

