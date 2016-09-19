from __future__ import unicode_literals

from django.apps import AppConfig


class AssetsConfig(AppConfig):
    name = 'assets'
    verbose_name = "Asset Management"
    def ready(self):
    	print("---------- STARTING ASSETS Application ------------")
    	pass # startup code here
