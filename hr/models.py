from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.conf import settings
import datetime

YEAR_CHOICES = []
for r in range(1980, (datetime.datetime.now().year+1)):
    YEAR_CHOICES.append((r,r))

def upoad_location(instance, filename):
	return "%s/%s" %(instance.employee_id, filename)

class Country(models.Model):
	country_code = models.CharField(blank=False, max_length=3)
	country_desc = models.CharField(blank=False,max_length=100)
	class Meta:
		permissions = (
            ('view_country', 'View Country'),
        )

	def __unicode__(self):
		return '%s' % (self.country_desc)

class Organization(models.Model):
	name = models.CharField(max_length=254,blank=False)
	location = models.CharField(max_length=100)
	#address = models.CharField(max_length=254)
	country = models.ForeignKey(Country)
	is_headoffice = models.BooleanField(default=False)
	class  Meta:
		permissions = (
            ('view_organization', 'View Organization'),
        )
	def __unicode__(self):
		return '%s' % (self.name)

class EmployeesDirectory(models.Model):
	firstname = models.CharField(max_length=100)
	lastname = models.CharField(max_length=100)
	employee_id = models.CharField(max_length=10)
	email = models.EmailField(max_length=254)
	organization = models.ForeignKey(Organization)
	employment_type = models.CharField(max_length=20,null=True,blank=True,choices=settings.EMPLOYMENT_TYPE_CHOICES,default=settings.DEFAULT_EMPLOYMENT_TYPE)	
	is_active= models.BooleanField(default=True)
	designation = models.CharField(max_length=100)
	manager = models.ForeignKey("self", null=True,blank=True)
	is_manager = models.BooleanField(default=False)
	role = models.CharField(max_length=25, choices=settings.USER_GROUP_CHOICES, default=settings.DEFAULT_USER_GROUP_CHOICE)
	assets_privilege = models.CharField(max_length=25, choices=settings.ASSET_PRIVILEGES_CHOICES, default=settings.DEFAULT_ASSET_PRIVILEGES_CHOICE)
	user = models.OneToOneField('auth.user', on_delete=models.CASCADE)
	image = models.FileField(upload_to=upoad_location, null=True,blank=True)
	def __unicode__(self):
		return '{0} {1}'.format(self.firstname, self.lastname)
	def get_absolute_url(self):
		return reverse( "hr:empDetail", kwargs={"id" : self.id } )
	def __str__(self):
		return "%s %s" % (self.firstname, self.lastname)
	class Meta:
		ordering = ["firstname", "lastname"]
		permissions = (
            ('view_employeesdirectory', 'View Employees'),
            ('view_employee_info', 'View Employee Info'),
        )

class Department(models.Model):
	hod = models.ForeignKey(EmployeesDirectory)
	name = models.CharField(max_length=100)
	def __unicode__(self):
		return self.name

class EmploymentHistory(models.Model):
	employee = models.ForeignKey(EmployeesDirectory, on_delete=models.CASCADE)
	date_joined = models.DateField(auto_now=False,auto_now_add=False)

# LeaveAccurals  model will store current leave balances 
# for each employee under each leave type
class LeaveAccurals(models.Model):
	employee = models.ForeignKey(EmployeesDirectory, on_delete=models.CASCADE)
	leaveType = models.CharField(max_length=25, choices=settings.LEAVE_TYPE_CHOICES, default=settings.DEFAULT_LEAVE_TYPE)
	accuredLeaves = models.DecimalField(max_digits=4,decimal_places=2,default=0)
	last_update_timestamp = models.DateTimeField(auto_now=True,auto_now_add=False)
	class Meta:
		permissions = (
            ('view_leaveaccurals', 'View Leave Accural Info'),
            ('edit_leaveaccurals', 'Edit Leave Accural Details'),
        )
	def __str__(self):
		return "%s - %s" %(self.leaveType, self.accuredLeaves)

class Holidays(models.Model):
	description = models.CharField(max_length=254, blank=False)
	date = models.DateField(auto_now=False, auto_now_add=False)
	country = models.ForeignKey(Country)
	year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year)
	class Meta:
		permissions = (
            ('view_holidays', 'View Holidays'),
        )
	def __unicode__(self):
		return '%s' % (self.description)

# Leaves model:
# This model will store complete history of Leave process workflow
class Leaves(models.Model):
	employee_id = models.ForeignKey(EmployeesDirectory)
	leaveType = models.CharField(max_length=25, choices=settings.LEAVE_TYPE_CHOICES, default=settings.DEFAULT_LEAVE_TYPE)
	startedDate = models.DateField(auto_now=False,auto_now_add=False)
	endDate = models.DateField(auto_now=False,auto_now_add=False)
	numberOfDays = models.DecimalField(max_digits=4,decimal_places=2,default=0)
	status = models.CharField(max_length=25, choices=settings.LEAVE_STATUS_CHOICES, default=settings.LEAVE_DEFAULT_STATUS)
	reason = models.CharField(max_length=254)
	rejection_reason = models.TextField(max_length=300)
	currentProject = models.CharField(max_length=254)
	creation_timestamp = models.DateTimeField(auto_now=False,auto_now_add=True)
	last_update_timestamp = models.DateTimeField(auto_now=True,auto_now_add=False)
	class Meta:
		permissions = (
            ('view_leaves', 'View Leaves'),
        )
	def __str__(self):
		return "%s - %s [%s]" %(self.leaveType, self.reason, self.status)
		
