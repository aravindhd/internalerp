from django.conf.urls import url
from . import views

urlpatterns = [
	#url(r'^assets/$', views.assets_list, name='assets_list'),
	#url(r'^assets/$', views.assets_list, name='assets_list'),
	url(r'^categoryAdd/$', views.asset_category_add, name='asset_category_add'),
	url(r'^categories/$', views.asset_categories, name='asset_categories'),
	url(r'^add/$', views.asset_add, name='asset_add'),
	url(r'^view/$', views.assets_view, name='assets_view'),
	url(r'^assigned/$', views.assets_assigned, name='assets_assigned'),
	url(r'^instock/$', views.assets_instock, name='assets_instock'),
	url(r'^details/(?P<id>[0-9]+)/$', views.asset_details, name='asset_details'),
	url(r'^update/(?P<id>[0-9]+)/$', views.asset_update, name='asset_update'),
	url(r'^assetsPerEmployee/(?P<id>[0-9]+)/$', views.assets_per_employee, name='assets_per_employee'),
	url(r'^myAssets/$', views.myassets, name='myassets'),
	url(r'^avail/$', views.asset_avail, name='asset_avail'),
	url(r'^getAssetsByCategory/$', views.get_assets_by_category, name='get_assets_by_category'),
]