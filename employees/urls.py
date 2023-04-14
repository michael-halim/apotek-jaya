from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views
from employees.views import EmployeesView

app_name = 'employees'
urlpatterns = [
    path('',views.EmployeesView.as_view(), name='employees'),
    path('fetch-employees/',views.FetchEmployees.as_view(), name='fetch-employees'),
    path('create/',views.CreateEmployeesView.as_view(), name='create-employees'),
    path('update/<str:employee_uuid>',views.UpdateEmployeesView.as_view(), name='update-employees'),
]
urlpatterns += staticfiles_urlpatterns()
