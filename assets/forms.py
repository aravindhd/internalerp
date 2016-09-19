import math
from django import forms
from .models import AssetCategories, Assets
from tagging.forms import TagField

class assetCategoryForm(forms.ModelForm):
	class Meta:
		model = AssetCategories
		fields = [ 'category', 'description' ]
		labels = {
            'category' : 'Asset category',
            'description' : 'Description',
        }

class assetForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(assetForm, self).__init__(*args, **kwargs)
		if self.fields['status'] != 'ASSIGNED':
			self.fields['assignmentCategory'].widget.attrs['disabled'] = True
			self.fields['assignedTo'].widget.attrs['disabled'] = True
			self.fields['assignedDate'].widget.attrs['disabled'] = True
			self.fields['status'].widget.attrs['onclick'] = 'updateAssignmentElements(this);'
			pass
	def clean(self):
		print("----- FORM CLEAN ------")
		errors = []
		'''
		#Example Error 
		status = self.cleaned_data.get('status')
		if status != 'ASSIGNED':
			err = "[ Assigned To must be defaulted while status is NOT ASSIGNED ]"
			self._errors["invalid_form"] = err
			errors.append(err)
		'''
		if len(errors):
			raise forms.ValidationError(' & '.join(errors))
		else:
			return self.cleaned_data
	class Meta:
		model = Assets
		fields = [ 'assetId', 
					'name',
					'category',
					'model',
					'serialNumber',
					'manufacturer',
					'description',
					'status',
					'assignmentCategory',
					'assignedTo',
					'assignedDate',
					'tags'
				]
		widgets = {
			'assignedDate' : forms.DateInput(attrs={'class' : 'date_picker'})
		}
		labels = {
            'assetId' : 'Asset ID',
            'name' : 'Name',
            'category' : 'Category',
            'model' : 'Model',
            'serialNumber' : 'Serial Number #',
            'manufacturer' : 'Manufacturer / Vendor',
            'description' : 'Description',
            'status' : 'Status',
            'assignmentCategory' : 'Assignment Category',
            'assignedTo' : 'Assigned To',
            'assignedDate' : 'Assigned Date',
            'tags' : 'Tags(space separated)'
        }