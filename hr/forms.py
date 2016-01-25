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
			"is_manager",
			"employment_type",
			"designation",
			"is_active",
			"image"
			]
		labels = {
            'firstname': 'Firstname',
            'lastname': 'Lastname',
            'employee_id': 'Employee ID',
            'email': 'Email Address',
            'employment_type': 'Job Type',
            'designation': 'Designation',
            'is_manager' : 'Is Manager',
            'is_active': 'Is Active',
            'image' : 'Employee Image',
        }

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

class leaveAccuralForm(forms.Form):
	pl = forms.DecimalField(label='Privilege Leave', min_value=0,max_value=12,max_digits=4,decimal_places=2,)
	cl = forms.DecimalField(label='Casual Leave', min_value=0,max_value=12,max_digits=4,decimal_places=2,)
	sl = forms.DecimalField(label='Sick Leave', min_value=0,max_value=12,max_digits=4,decimal_places=2,)
	compoff = forms.DecimalField(label='Compensation Leave', min_value=0,max_digits=4,decimal_places=2,)
	wfh = forms.DecimalField(label='Work From Home', min_value=0,max_value=3,max_digits=4,decimal_places=2,)
	lop = forms.DecimalField(label='Unpaid Leaves', min_value=0,max_digits=4,decimal_places=2,)
