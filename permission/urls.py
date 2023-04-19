from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'permission'
urlpatterns = [
    path('',views.PermissionView.as_view(), name='permission'),
    path('list-permission/',views.ListPermissionView.as_view(), name='list-permission'),
    path('create/',views.CreatePermissionView.as_view(), name='create-permission'),
    # path('detail/<str:employee_uuid>',views.DetailPermissionView.as_view(), name='detail-permission'),
    # path('update/<str:employee_uuid>',views.UpdatePermissionView.as_view(), name='update-permission'),
    # path('delete/<str:employee_uuid>',views.DeletePermissionView.as_view(), name='delete-permission'),
]
urlpatterns += staticfiles_urlpatterns()