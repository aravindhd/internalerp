from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.conf import settings
from tagging.registry import register
from tagging.fields import TagField
import datetime
from hr.models import EmployeesDirectory
# Create your models here.

class AssetCategories(models.Model):
	category = models.CharField(blank=False, unique=True, max_length=30)
	description = models.CharField(blank=False, max_length=100)
	class Meta:
		permissions = (
            ('view_asset_categories', 'View Asset Categories'),
        )
	def __unicode__(self):
		return '%s' % (self.category)

class Assets(models.Model):
	assetId = models.CharField(max_length=20)
	name = models.CharField(max_length=100)
	category = models.ForeignKey(AssetCategories)
	model = models.CharField(max_length=100)
	serialNumber = models.CharField(max_length=100)
	manufacturer = models.CharField(max_length=100)
	description = models.CharField(max_length=100)
	status = models.CharField(max_length=25, choices=settings.ASSET_STATUS_CHOICES, default=settings.ASSET_DEFAULT_STATUS)
	assignmentCategory = models.CharField(max_length=25, choices=settings.ASSET_ASSIGNMENT_CATEGORY, default=settings.ASSET_DEFAULT_ASSIGNMENT_CATEGORY)
	assignedTo = models.ForeignKey(EmployeesDirectory)
	assignedDate = models.DateTimeField(auto_now=False, auto_now_add=False)
	creationTimestamp = models.DateTimeField(auto_now=False,auto_now_add=True)
	lastUpdateTimestamp = models.DateTimeField(auto_now=True,auto_now_add=False)
	tags = TagField()
	class Meta:
		ordering = ["assetId", "category", "name"]
		permissions = (
            ('view_assets', 'View Assets'),
        )
	def __str__(self):
		return "%s %s %s" %(self.assetId, self.name, self.category)
	def get_tags(self):
		return Tag.objects.get_for_object(self) 

# Registering the model in Tagging application
#register(Assets)