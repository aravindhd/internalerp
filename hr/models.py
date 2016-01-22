from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.conf import settings

def upoad_location(instance, filename):
	return "%s/%s" %(instance.id, filename)

class EmployeesDirectory(models.Model):
	firstname = models.CharField(max_length=100)
	lastname = models.CharField(max_length=100)
	employee_id = models.CharField(max_length=10)
	email = models.EmailField(max_length=254)
	#department = models.ForeignKey("Department")
	manager = models.ForeignKey("self", null=True,blank=True)
	employment_type = models.CharField(max_length=20, null=True, blank=True, choices=settings.EMPLOYMENT_TYPE_CHOICES)	
	designation = models.CharField(max_length=100)
	#role = models.IntegerField(default=0)
	user = models.OneToOneField('auth.user')
	image = models.FileField(upload_to=upoad_location, null=True,blank=True)
	def __unicode__(self):
		return '{0} {1}'.format(self.firstname, self.lastname)
	def get_absolute_url(self):
		return reverse( "hr:empDetail", kwargs={"id" : self.id } )
	def __str__(self):
		return self.fullname
	class Meta:
		ordering = ["firstname", "lastname"]

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
	accuredLeaves = models.IntegerField(default=12)
	last_update_timestamp = models.DateTimeField(auto_now=True,auto_now_add=False)

# Leaves model:
# This model will store complete history of Leave process workflow
class Leaves(models.Model):
	employee_id = models.ForeignKey(EmployeesDirectory)
	leaveType = models.CharField(max_length=25, choices=settings.LEAVE_TYPE_CHOICES, default=settings.DEFAULT_LEAVE_TYPE)
	startedDate = models.DateField(auto_now=False,auto_now_add=False)
	endDate = models.DateField(auto_now=False,auto_now_add=False)
	numberOfDays = models.IntegerField(default=0)
	status = models.CharField(max_length=25, choices=settings.LEAVE_STATUS_CHOICES, default=settings.LEAVE_DEFAULT_STATUS)
	reason = models.TextField(max_length=508)
	currentProject = models.CharField(max_length=254)
	creation_timestamp = models.DateTimeField(auto_now=False,auto_now_add=True)
	last_update_timestamp = models.DateTimeField(auto_now=True,auto_now_add=False)

	def __str__(self):
		return "%s - %s [%s]" %(self.leaveType, self.reason, self.status)
		
