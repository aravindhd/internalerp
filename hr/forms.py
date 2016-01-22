from django import forms
from .models import EmployeesDirectory, Department, EmploymentHistory, LeaveAccurals, Leaves

class employeeForm(forms.ModelForm):
	class Meta:
		model = EmployeesDirectory
		fields = [
			"firstname",
			"lastname",
			"employee_id",
			"email",
			"manager",
			#"department",
			"employment_type",
			"designation",
			"user",
			"image"
			]
		#widgets = {
        #    'name': Textarea(attrs={'cols': 80, 'rows': 20}),
        #}
		labels = {
            'firstname': 'Firstname',
            'lastname': 'Lastname',
            'employee_id': 'Employee ID',
            'email': 'Email Address',
            'employment_type': 'Job Type',
            'designation': 'Designation',
            'user': 'Mapped User Account',
            'image' : 'Employee Image',
        }
        #help_texts = {
        #    'name': _('Some useful help text.'),
        #}
        #error_messages = {
        #    'name': {
        #        'max_length': _("This writer's name is too long."),
        #    },
        #}

class leaveForm(forms.ModelForm):
	class Meta:
		model = Leaves
		fields = [
			"employee_id",
			"leaveType",
			"reason",
			"startedDate",
			"endDate",
			"status",
			"numberOfDays",
			"currentProject"
			]
		widgets = {
			'startedDate' : forms.DateInput(attrs={'class' : 'date_picker'}),
			'endDate' : forms.DateInput(attrs={'class' : 'date_picker'})
		}
		labels = {
            'employee_id': 'Employee',
            'leaveType': 'Leave Type',
            'reason' : 'Reason',
            'startedDate' : 'Date From',
            'endDate' : 'Date To',
            'numberOfDays' : '# Days',
            'currentProject' : 'Project',
        }