from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.employees_list, name='employees_list'),
    url(r'^empTable/$', views.employees_table, name='employees_table'), # same as employees_list only views are different
    url(r'^empDetail/(?P<id>[0-9]+)/$', views.employee_details, name='employee_details'),
    url(r'^empUpdate/(?P<id>[0-9]+)/$', views.employee_update, name='employee_update'),
    url(r'^empDelete/(?P<id>[0-9]+)/$', views.employee_delete, name='employee_delete'),
    url(r'^empCreate/$', views.employee_create, name='employee_create'),
    url(r'^leaves/$', views.leaves_list, name='leaves_list'),
    url(r'^leaveDetail/(?P<id>[0-9]+)/$', views.leave_details, name='leave_details'),
    url(r'^leaveCreate/$', views.leave_create, name='leave_create'),
    url(r'^leaveUpdate/(?P<id>[0-9]+)/$', views.leave_update, name='leave_update'),
    url(r'^empleaves/$', views.employee_leaves, name='employee_leaves'),

    url(r'^leavesAllocate/$', views.leaves_allocate, name='leaves_allocate'),
    url(r'^empInfo/$', views.employee_info, name='employee_info'),
]