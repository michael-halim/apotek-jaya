from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'settings'
urlpatterns = [
    path('',views.SettingsView.as_view(), name='settings'),
    path('fetch-settings/',views.ListSettingsView.as_view(), name='fetch-settings'),
    path('create',views.CreateSettingsView.as_view(), name='create-settings'),
    path('detail',views.DetailSettingsView.as_view(), name='detail-settings'),
    path('update',views.UpdateSettingsView.as_view(), name='update-settings'),
    
]
urlpatterns += staticfiles_urlpatterns()
