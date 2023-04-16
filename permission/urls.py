from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'permission'
urlpatterns = [
    path('',views.PermissionView.as_view(), name='permission'),
    path('list-permission/',views.ListPermissionView.as_view(), name='list-permission'),
]
urlpatterns += staticfiles_urlpatterns()
