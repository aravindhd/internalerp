from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^employees/$', views.employees_list, name='employees_list'),
    url(r'^myemployees/$', views.employees_list_per_manager, name='employees_list_per_manager'),
    url(r'^empTable/$', views.employees_table, name='employees_table'), # same as employees_list only views are different
    url(r'^empDetail/(?P<id>[0-9]+)/$', views.employee_details, name='employee_details'),
    url(r'^empUpdate/(?P<id>[0-9]+)/$', views.employee_update, name='employee_update'),
    url(r'^empDelete/(?P<id>[0-9]+)/$', views.employee_delete, name='employee_delete'),
    url(r'^empCreate/$', views.employee_create, name='employee_create'),
    url(r'^leaves/$', views.leaves_list, name='leaves_list'),
    url(r'^myempleaves/$', views.leaves_list_per_manager, name='leaves_list_per_manager'),
    url(r'^leaveDetail/(?P<id>[0-9]+)/$', views.leave_details, name='leave_details'),
    url(r'^leaveCreate/$', views.leave_create, name='leave_create'),
    url(r'^leaveUpdate/(?P<id>[0-9]+)/$', views.leave_update, name='leave_update'),
    url(r'^empleaves/$', views.employee_leaves, name='employee_leaves'),
    url(r'^holidays/$', views.view_holidays, name='view_holidays'),
    url(r'^holidays/add/$', views.add_holiday, name='add_holiday'),
    url(r'^countryConfigure/$', views.country_configure, name='country_configure'),
    url(r'^countries/$', views.country_list, name='country_list'),
    url(r'^orgConfigure/$', views.organization_configure, name='organization_configure'),
    url(r'^organizations/$', views.organization_list, name='org_list'),

    url(r'^leavesAllocate/$', views.leaves_allocate, name='leaves_allocate'),
    url(r'^empInfo/$', views.employee_info, name='employee_info'),
    url(r'^$', views.employee_info, name='employee_info'),
]