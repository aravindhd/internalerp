import math
from django import forms
from .models import AssetCategories, Assets, AvailAsset
from tagging.forms import TagField

class assetCategoryForm(forms.ModelForm):
	class Meta:
		model = AssetCategories
		fields = [ 'category', 'description', 'enable_asset_avail_workflow' ]
		labels = {
            'category' : 'Asset category',
            'description' : 'Description',
            'enable_asset_avail_workflow' : 'Enable Asset Avail Workflow'
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

class availAssetForm(forms.Form):
	AssetCategory = forms.ModelChoiceField(queryset=AssetCategories.objects.filter(enable_asset_avail_workflow=True),required=True, label='Asset Category')
	Asset = forms.ChoiceField(required=True)
	AvailTime = forms.DateTimeField(label='Avail Date Time')
	def __init__(self, *args, **kwargs):
		super(availAssetForm, self).__init__(*args, **kwargs)
		self.fields['AssetCategory'].widget.attrs['onclick'] = 'updateAssetElements(this);'
		self.fields['AvailTime'].widget.attrs['class'] = 'datetime_picker'
		pass
	def clean(self):
		pass

class availedAssetUpdateForm(forms.ModelForm):
	status = forms.ChoiceField(choices=(), required=True)
	def __init__(self, userBased_Status_choices, isUserRole, *args, **kwargs):
		super(availedAssetUpdateForm, self).__init__(*args, **kwargs)
		self.fields['status'].choices = userBased_Status_choices
		self.fields['id'].widget.attrs['readonly'] = True
		if isUserRole == 'manager':
			self.fields['assetId'].widget.attrs['class'] = 'readOnlySelect'
			self.fields['availed_datetime'].widget.attrs['readonly'] = True
			self.fields['returned_datetime'].widget.attrs['readonly'] = True
		elif isUserRole == 'validator':
			self.fields['assetId'].widget.attrs['class'] = 'readOnlySelect'
			self.fields['availed_datetime'].widget.attrs['readonly'] = True 
		pass
	def clean(self):
		pass
	class Meta:
		model = AvailAsset
		fields = [ 'id' , 'assetId' , 'status', 'availed_datetime', 'returned_datetime', ]
		widgets = {
			'availed_datetime' : forms.DateTimeInput(attrs={'class' : 'date_picker'}),
			'returned_datetime' : forms.DateTimeInput(attrs={'class' : 'date_picker'})
		}
		labels = {
			'id' : 'Unique ID',
            'assetId' : 'Asset',
            'status' : 'Status',
            'availed_datetime' : 'Avail Date Time',
            'returned_datetime' : 'Return Date Time',
        }