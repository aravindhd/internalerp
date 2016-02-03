from __future__ import unicode_literals

from django.apps import AppConfig
#from django.contrib.auth.models import User, Group

class HrConfig(AppConfig):
    name = 'hr'
    verbose_name = "HR App"
    def ready(self):
    	print("---------- STARTING HR Application ------------")
    	#groups = Group.objects.all()
    	#print(groups)
    	#group = Group.objects.create(name='employees')
    	pass # startup code here