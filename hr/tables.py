import django_tables2 as tables
from django.utils.safestring import mark_safe
from django.utils.html import escape
from hr.models import EmployeesDirectory, Department, EmploymentHistory, LeaveAccurals, Leaves
import itertools

class ImageColumn(tables.Column):
	def render(self, value):
		return mark_safe('<img class="img-circle img-responsive" src="/media/%s" style="width:40px;height:40px" />' % escape(value))

class EmployeesTable(tables.Table):
	row_number = tables.Column(empty_values=(), verbose_name="#", orderable=False)
	image = ImageColumn(verbose_name="", orderable=False)
	employee_id = tables.Column(verbose_name="Employeed ID")
	firstname = tables.Column(verbose_name="First Name")
	lastname = tables.Column(verbose_name="Last Name")
	email = tables.Column(verbose_name="Email")
	manager = tables.Column(verbose_name="Manager")
	employment_type = tables.Column(verbose_name="Job Type")
	designation = tables.Column(verbose_name="Designation")
	user = tables.Column(verbose_name="User Account")

	def __init__(self, *args, **kwargs):
		super(EmployeesTable, self).__init__(*args, **kwargs)
		self.counter = itertools.count()

	def render_row_number(self):
		return '%d' % next(self.counter)

	class Meta:
		model = EmployeesDirectory
		exclude = ("id", )
		attrs =  { "class" : "paleblue" }
		sequence = ( "row_number", "image", "employee_id", "firstname", "lastname", "email", "manager", "employment_type", "designation", "user")