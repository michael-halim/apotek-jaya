from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'permission'
urlpatterns = [
    path('',views.PermissionView.as_view(), name='permission'),
    path('list-permission/',views.ListPermissionView.as_view(), name='list-permission'),
    path('create/',views.CreatePermissionView.as_view(), name='create-permission'),
    path('detail/<str:employee_uuid>',views.DetailPermissionView.as_view(), name='detail-permission'),
    path('update/<str:employee_uuid>',views.UpdatePermissionView.as_view(), name='update-permission'),
    path('delete/<str:employee_uuid>',views.DeletePermissionView.as_view(), name='delete-permission'),

    path('group/',views.PermissionGroupView.as_view(), name='permission-group'),
    path('group/list-permission-group/',views.ListPermissionGroupView.as_view(), name='list-permission-group'),
    path('group/create',views.CreatePermissionGroupView.as_view(), name='create-permission-group'),
    path('group/detail/<str:group_id>',views.DetailPermissionGroupView.as_view(), name='detail-permission-group'),
    path('group/update/<str:group_id>',views.UpdatePermissionGroupView.as_view(), name='update-permission-group'),
    path('group/delete/<str:group_id>',views.DeletePermissionGroupView.as_view(), name='delete-permission-group'),

]
urlpatterns += staticfiles_urlpatterns()