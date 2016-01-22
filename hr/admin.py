from django.contrib import admin
from .models import EmployeesDirectory, Department, EmploymentHistory, LeaveAccurals, Leaves
# Register your models here.

admin.site.register(EmployeesDirectory)
admin.site.register(Department)
admin.site.register(EmploymentHistory)
admin.site.register(LeaveAccurals)
admin.site.register(Leaves)
