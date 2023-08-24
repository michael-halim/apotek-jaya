from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'overtimes'
urlpatterns = [
    path('',views.OvertimesView.as_view(), name='overtimes'),
    path('fetch-overtimes/',views.ListOvertimesView.as_view(), name='fetch-overtimes'),
    path('create/',views.CreateOvertimesView.as_view(), name='create-overtimes'),
    path('detail/<str:overtime_uuid>',views.DetailOvertimesView.as_view(), name='detail-overtimes'),
    path('delete/<str:overtime_uuid>',views.DeleteOvertimesView.as_view(), name='delete-overtimes'),
    path('update/<str:overtime_uuid>',views.UpdateOvertimesView.as_view(), name='update-overtimes'),
    path('add-overtimes-users/',views.AddOvertimesUsersView.as_view(), name='add-overtimes-users'),
]
urlpatterns += staticfiles_urlpatterns()
