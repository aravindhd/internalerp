from django import forms
from .models import Country, Organization
from .models import EmployeesDirectory, Department, EmploymentHistory
from .models import LeaveAccurals, Leaves, Holidays
from decimal import Decimal
from workdays import networkdays

class organizationForm(forms.ModelForm):
	class Meta:
		model = Organization
		fields = ['name', 'location', 'country', 'is_headoffice' ]
		labels = {
            'name': 'Organization Name',
            'is_headoffice' : 'Is HeadOffice',
        }

class countryForm(forms.ModelForm):
	class Meta:
		model = Country
		fields = [ 'country_code', 'country_desc' ]
		labels = {
            'country_code' : 'Country Code',
            'country_desc' : 'Country Name',
        }

class employeeForm(forms.ModelForm):
	class Meta:
		model = EmployeesDirectory
		fields = [
			"firstname",
			"lastname",
			"employee_id",
			"email",
			"organization",
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

class holidaysForm(forms.ModelForm):
	class Meta:
		model = Holidays
		fields = [ 'description', 'date', 'country' ]
		widgets = {
			'date' : forms.DateInput(attrs={'class' : 'date_picker'})
		}

class leaveRequestForm(forms.ModelForm):
	def __init__(self, isEmployeeReq,  *args, **kwargs):
		super(leaveRequestForm, self).__init__(*args, **kwargs)
		if isEmployeeReq:
			self.fields['employee_id'].widget.attrs['class'] = 'readOnlySelect'

	def clean(self):
		print(">>>>>> leaveRequestForm clean() definition ......")
		emp = self.cleaned_data.get('employee_id')
		lType = self.cleaned_data.get('leaveType')
		fromDate = self.cleaned_data.get('startedDate')
		endDate = self.cleaned_data.get('endDate')
		numDays = self.cleaned_data.get('numberOfDays')
		empAccuredLeaves = LeaveAccurals.objects.get(employee=emp, leaveType=lType).accuredLeaves
		holidays = Holidays.objects.filter(country=emp.organization.country).values('date')
		empHolidays = []
		for holiday in holidays:
			empHolidays.append(holiday['date'])
		numberBusinessDays = networkdays(fromDate, endDate, empHolidays)
		errors = []
		if endDate < fromDate:
			err = "[ End date cannot be earlier than start date ]"
			self._errors["invalid_dates"] = err
			errors.append(err)			
		if ( Decimal(empAccuredLeaves) < Decimal(numDays) ):
			err = "[ Employee do not have sufficient leave balance under %s category ]" %(lType)
			self._errors["balance_error"] = err
			errors.append(err)
		if Decimal(numDays) > Decimal(numberBusinessDays):
			err = "[ Provide valid number of days considering weekends and holidays ]"
			self._errors["invalid_numdays"] = err
			errors.append(err)

		if len(errors):
			raise forms.ValidationError(' & '.join(errors))
		else:
			return self.cleaned_data

	def save(self, commit=False):
		print(">>>>>> leaveRequestForm SAVE Override....")		
		leaveReqForm = super(leaveRequestForm, self).save(commit=False)
		
		# Update the Leave Accural balance and save this form
		emp = self.cleaned_data.get('employee_id')
		lType = self.cleaned_data.get('leaveType')
		numDays = self.cleaned_data.get('numberOfDays')
		empAccBalance = LeaveAccurals.objects.get(employee=emp, leaveType=lType).accuredLeaves
		newAccLeaveBalance = Decimal(empAccBalance) - Decimal(numDays)
		LeaveAccurals.objects.filter(employee=emp, leaveType=lType).update(accuredLeaves=newAccLeaveBalance)
		
		# Saving the leave request info
		leaveReqForm.save()
		return leaveReqForm

	class Meta:
		model = Leaves
		fields = [
			"employee_id",
			"leaveType",
			"startedDate",
			"endDate",
			"numberOfDays",
			"reason",
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

class leaveEditForm(forms.ModelForm):
	status = forms.ChoiceField(choices=(), required=True)
	rejection_reason = forms.CharField(max_length=300, required=False)

	def __init__(self, userBased_Status_choices, isUserRole, *args, **kwargs):
		super(leaveEditForm, self).__init__(*args, **kwargs)
		self.fields['status'].choices = userBased_Status_choices
		self.fields['leaveType'].widget.attrs['class'] = 'readOnlySelect'

		if isUserRole == 'manager':
			self.fields['startedDate'].widget.attrs['readonly'] = True
			self.fields['endDate'].widget.attrs['readonly'] = True
			self.fields['numberOfDays'].widget.attrs['readonly'] = True
			self.fields['reason'].widget.attrs['readonly'] = True
		elif isUserRole == 'employee':
			self.fields['rejection_reason'].widget.attrs['readonly'] = True
    
	def clean(self):
		print(">>>>>> leaveEditForm clean() definition ......")
		emp = self.cleaned_data.get('employee_id')
		lType = self.cleaned_data.get('leaveType')
		fromDate = self.cleaned_data.get('startedDate')
		endDate = self.cleaned_data.get('endDate')
		numDays = self.cleaned_data.get('numberOfDays')
		empAccuredLeaves = LeaveAccurals.objects.get(employee=emp, leaveType=lType).accuredLeaves
		holidays = Holidays.objects.filter(country=emp.organization.country).values('date')
		empHolidays = []
		for holiday in holidays:
			empHolidays.append(holiday['date'])
		numberBusinessDays = networkdays(fromDate, endDate, empHolidays)
		errors = []
		if endDate < fromDate:
			err = "[ End date cannot be earlier than start date ]"
			self._errors["invalid_dates"] = err
			errors.append(err)			
		if ( Decimal(empAccuredLeaves) < Decimal(numDays) ):
			err = "[ Employee do not have sufficient leave balance under %s category ]" %(lType)
			self._errors["balance_error"] = err
			errors.append(err)
		if Decimal(numDays) > Decimal(numberBusinessDays):
			err = "[ Provide valid number of days considering weekends and holidays ]"
			self._errors["invalid_numdays"] = err
			errors.append(err)

		if len(errors):
			raise forms.ValidationError(' & '.join(errors))
		else:
			return self.cleaned_data

	def save(self, commit=False):
		print(">>>>>> leaveEditForm SAVE Override....")
		#print(self.instance.id) # To get the db stored value
		leaveUpdForm = super(leaveEditForm, self).save(commit=False)
		
		# Update the Leave Accural balance and save this form
		emp = self.cleaned_data.get('employee_id')
		lType = self.cleaned_data.get('leaveType')
		newNumDays = self.cleaned_data.get('numberOfDays')
		status = self.cleaned_data.get('status')
		empAccBalance = LeaveAccurals.objects.get(employee=emp, leaveType=lType).accuredLeaves
		oldLeaveCount = Leaves.objects.get(id=self.instance.id).numberOfDays
		doUpdate = False
		if (status == 'REJECTED') or (status == 'DISCARD'):
			newAccLeaveBalance = Decimal(empAccBalance) + Decimal(oldLeaveCount)	# Revert the leave balance
			doUpdate = True
		else:
			if (oldLeaveCount != newNumDays):	# if there is change only in dates/days, updating leaveBalance
				newAccLeaveBalance = (Decimal(empAccBalance) + Decimal(oldLeaveCount))- Decimal(newNumDays)
				doUpdate = True
			#else:
			#	newAccLeaveBalance = Decimal(empAccBalance) - Decimal(newNumDays)
		#TODO:
		# Cover use-cases: Reject-Re-Open-Approve
		# - user submit-re-open- provide leave count > accural -submit
		
		# Update only if there is any change to leave balance
		if doUpdate:
			LeaveAccurals.objects.filter(employee=emp, leaveType=lType).update(accuredLeaves=newAccLeaveBalance)
		
		# Saving the leave request info
		leaveUpdForm.save()
		return leaveUpdForm

	class Meta:
		model = Leaves
		fields = [
			"employee_id",
			"leaveType",
			"startedDate",
			"endDate",
			"numberOfDays",
			"status",
			"reason",
			"currentProject",
			"rejection_reason",
			]
		widgets = {
			#'employee_id' : forms.Select(attrs={'readonly' : True, 'disabled' : True }), # DONOT USE THIS
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

class singleEmployeeLeaveAccuralForm(forms.Form):
	employee = forms.ModelChoiceField(queryset=EmployeesDirectory.objects.all(),required=True,initial=0) 
	pl = forms.DecimalField(label='Privilege Leave', min_value=0,max_value=12,max_digits=4,decimal_places=2,initial=0)
	cl = forms.DecimalField(label='Casual Leave', min_value=0,max_value=12,max_digits=4,decimal_places=2,initial=0)
	sl = forms.DecimalField(label='Sick Leave', min_value=0,max_value=12,max_digits=4,decimal_places=2,initial=0)
	compoff = forms.DecimalField(label='Compensation Leave', min_value=0,max_digits=4,decimal_places=2,initial=0)
	wfh = forms.DecimalField(label='Work From Home', min_value=0,max_value=3,max_digits=4,decimal_places=2,initial=0)
	lop = forms.DecimalField(label='Unpaid Leaves', min_value=0,max_digits=4,decimal_places=2,initial=0)

class csvImportLeaveAccuralForm(forms.Form):
	csvFile = forms.FileField(required=False, label='CSV File')
