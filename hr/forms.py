import math
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
			"role",
			"assets_privilege",
			"is_active",
			"image",
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
            'role' : 'User Role',
            'assets_privilege' : 'Assets Privilege',
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
			#self.fields['employee_id'].widget.attrs['class'] = 'readOnlySelect'
                        self.fields['employee_id'].widget.attrs['style'] = 'pointer-events:none'

	def clean(self):
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
		print("Working Days: [%s]" % (Decimal(numberBusinessDays)))
		print("Num of Days : [%s]" % (Decimal(numDays)))
		frac, whole = math.modf(Decimal(numDays))
		errors = []
		if ( (frac != 0.0 ) and  ((frac > 0.5) or (frac < 0.5))):
			err = "[ Number of days must be either whole number or multiples of 0.5 ]"
			self._errors["invalid_numdays"] = err
			errors.append(err)
		if endDate < fromDate:
			err = "[ End date cannot be earlier than start date ]"
			self._errors["invalid_dates"] = err
			errors.append(err)
		if (Decimal(numDays) > Decimal(numberBusinessDays) or (Decimal(numberBusinessDays) - Decimal(numDays) > 0.5)):
			err = "[ Provide valid number of days considering weekends and holidays ]"
			self._errors["invalid_numdays"] = err
			errors.append(err)
		if (lType != "LOP") and ( Decimal(empAccuredLeaves) < Decimal(numDays) ):
			err = "[ Employee do not have sufficient leave balance under %s category ]" %(lType)
			self._errors["balance_error"] = err
			errors.append(err)

		if len(errors):
			raise forms.ValidationError(' & '.join(errors))
		else:
			return self.cleaned_data

	def save(self, commit=False):
		leaveReqForm = super(leaveRequestForm, self).save(commit=False)
		
		# Update the Leave Accural balance and save this form
		emp = self.cleaned_data.get('employee_id')
		lType = self.cleaned_data.get('leaveType')
		numDays = self.cleaned_data.get('numberOfDays')
		empAccBalance = LeaveAccurals.objects.get(employee=emp, leaveType=lType).accuredLeaves
		if lType == 'LOP':
			newAccLeaveBalance = Decimal(empAccBalance) + Decimal(numDays)
		else:
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
            'leaveType': 'Category',
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
		#self.fields['leaveType'].widget.attrs['class'] = 'readOnlySelect'

		if isUserRole == 'manager':
			self.fields['leaveType'].widget.attrs['class'] = 'readOnlySelect'
			self.fields['startedDate'].widget.attrs['readonly'] = True
			self.fields['endDate'].widget.attrs['readonly'] = True
			self.fields['numberOfDays'].widget.attrs['readonly'] = True
			self.fields['reason'].widget.attrs['readonly'] = True
		elif isUserRole == 'employee':
			self.fields['rejection_reason'].widget.attrs['readonly'] = True
			self.fields['leaveType'].widget.attrs['class'] = 'readOnlySelect'    
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

		prevNumDays = Leaves.objects.get(id=self.instance.id).numberOfDays

		empAccuredLeaves = (empAccuredLeaves + prevNumDays)
		frac, whole = math.modf(Decimal(numDays))

		errors = []
		if ( (frac != 0.0 ) and  ((frac > 0.5) or (frac < 0.5))):
			err = "[ Number of days must be either whole number or multiples of 0.5 ]"
			self._errors["invalid_numdays"] = err
			errors.append(err)
		if endDate < fromDate:
			err = "[ End date cannot be earlier than start date ]"
			self._errors["invalid_dates"] = err
			errors.append(err)
		if Decimal(numDays) > Decimal(numberBusinessDays):
			err = "[ Provide valid number of days considering weekends and holidays ]"
			self._errors["invalid_numdays"] = err
			errors.append(err)
		if (lType != "LOP") and ( Decimal(empAccuredLeaves) < Decimal(numDays) ):
			err = "[ Employee do not have sufficient leave balance under %s category ]" %(lType)
			self._errors["balance_error"] = err
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
		numDays = self.cleaned_data.get('numberOfDays')
		status = self.cleaned_data.get('status')
		empAccBalance = LeaveAccurals.objects.get(employee=emp, leaveType=lType).accuredLeaves

		prevNumDays = Leaves.objects.get(id=self.instance.id).numberOfDays
		prevStatus = Leaves.objects.get(id=self.instance.id).status
		prevLType = Leaves.objects.get(id=self.instance.id).leaveType
		prevEmpAccBalance = LeaveAccurals.objects.get(employee=emp, leaveType=prevLType).accuredLeaves

		revertAccuralUpdate = False
		doAccuralUpdate = False
		isFormDetailsChanged = False
		updatePrevLTypeAcc = False

		if( prevLType != lType):
			isFormDetailsChanged = True
			updatePrevLTypeAcc = True
			pass
		if(prevNumDays != numDays):
			isFormDetailsChanged = True
			pass

		if(prevStatus == status):
			revertAccuralUpdate = False
		else:
			if (status == 'REJECTED'): # Rejected
				revertAccuralUpdate = True
				pass
			elif ( ( (prevStatus == 'SUBMITTED')  or (prevStatus == 'REOPENED') or (prevStatus == 'APPROVED')) and \
					(status == 'DISCARD') ):
				revertAccuralUpdate = True
				pass
			elif ( (prevStatus == 'REJECTED') and \
					((status == 'REOPENED') or (status == 'SUBMITTED'))
				): # Submitted or ReOpened
				doAccuralUpdate = True
				pass
			else : # Approved or Closed
				if((isFormDetailsChanged == True) or (updatePrevLTypeAcc == True)):
					print("CASE : isFormDetailsChanged == True or updatePrevLTypeAcc == True...")
					pass
				pass

		if(revertAccuralUpdate == True): # Status got changed as Rejected/Discard so accrual need to revert
			# Ignore the form changes if any 
			# Revert the accrual update made for older form values only
			print("Status got changed as Rejected/Discard so accrual need to revert")
			if prevLType == 'LOP':
				newAccuralBalance = (Decimal(prevEmpAccBalance) - Decimal(prevNumDays))
			else:
				newAccuralBalance = (Decimal(prevEmpAccBalance) + Decimal(prevNumDays))
			LeaveAccurals.objects.filter(employee=emp, leaveType=prevLType).update(accuredLeaves=newAccuralBalance)
			pass
		else: 
			# Re-submission of rejected/discarded/submitted/reopened leaves, 
			# accrual need to reduced
			print(">>>>> doAccuralUpdate : %s..." % (doAccuralUpdate))
			if((isFormDetailsChanged == True) or (doAccuralUpdate==True)): # Form details changed
				print("Re-submission of rejected/discarded/submitted/reopened leaves : updatePrevLTypeAcc- %s" %(updatePrevLTypeAcc))
				newAccuralBalance = 0
				newCurrLTypeAccrual = Decimal(empAccBalance)
				if(updatePrevLTypeAcc == True): # Revert the accrual update made for older form values only
					if prevLType == 'LOP':
						newAccuralBalance = (Decimal(prevEmpAccBalance) - Decimal(prevNumDays))
					else:
						newAccuralBalance = (Decimal(prevEmpAccBalance) + Decimal(prevNumDays))
					print("Updating the Old Leave Type : %s with Accrual Balance %s..." %(prevLType, newAccuralBalance))
					LeaveAccurals.objects.filter(employee=emp, leaveType=prevLType).update(accuredLeaves=newAccuralBalance)
					pass
				elif((prevNumDays != numDays) and (doAccuralUpdate != True) ):
					if(lType == 'LOP'):
						newCurrLTypeAccrual = Decimal(empAccBalance) - Decimal(prevNumDays)
					else:
						newCurrLTypeAccrual = Decimal(empAccBalance) + Decimal(prevNumDays)

				newAccuralBalance = 0
				# Updating the accrual for current form values
				if(lType == 'LOP'):
					newAccuralBalance = Decimal(newCurrLTypeAccrual) + Decimal(numDays)
				else:
					newAccuralBalance = Decimal(newCurrLTypeAccrual) - Decimal(numDays)
				print("Updating the CURRENT Leave Type : %s with Accrual Balance : %s..." % (lType, newAccuralBalance))
				LeaveAccurals.objects.filter(employee=emp, leaveType=lType).update(accuredLeaves=newAccuralBalance)
				# Revert the accrual update made for current form values only
				pass
			pass
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
	cl = forms.DecimalField(label='Casual Leave', min_value=0,max_value=12,max_digits=4,decimal_places=2,)
	pl = forms.DecimalField(label='Privilege Leave', min_value=0,max_value=12,max_digits=4,decimal_places=2,)
	sl = forms.DecimalField(label='Sick Leave', min_value=0,max_value=12,max_digits=4,decimal_places=2,)
	compoff = forms.DecimalField(label='Compensation Leave', min_value=0,max_digits=4,decimal_places=2,)
	lop = forms.DecimalField(label='Unpaid Leaves', min_value=0,max_digits=4,decimal_places=2,)
	wfh = forms.DecimalField(label='Work From Home', min_value=0,max_value=6,max_digits=4,decimal_places=2,)

class singleEmployeeLeaveAccuralForm(forms.Form):
	employee = forms.ModelChoiceField(queryset=EmployeesDirectory.objects.all(),required=True,initial=0) 
	cl = forms.DecimalField(label='Casual Leave', min_value=0,max_value=12,max_digits=4,decimal_places=2,initial=0)
	pl = forms.DecimalField(label='Privilege Leave', min_value=0,max_value=12,max_digits=4,decimal_places=2,initial=0)
	sl = forms.DecimalField(label='Sick Leave', min_value=0,max_value=12,max_digits=4,decimal_places=2,initial=0)
	compoff = forms.DecimalField(label='Compensation Leave', min_value=0,max_digits=4,decimal_places=2,initial=0)
	lop = forms.DecimalField(label='Unpaid Leaves', min_value=0,max_digits=4,decimal_places=2,initial=0)
	wfh = forms.DecimalField(label='Work From Home', min_value=0,max_value=6,max_digits=4,decimal_places=2,initial=0)

class csvImportLeaveAccuralForm(forms.Form):
	csvFile = forms.FileField(required=False, label='CSV File')
