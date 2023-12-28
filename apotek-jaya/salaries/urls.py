from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'salaries'
urlpatterns = [
    path('',views.SalariesView.as_view(), name='salaries'),
    path('fetch-salaries/',views.ListSalariesView.as_view(), name='fetch-salaries'),
    path('fetch-period/',views.FetchPeriodsView.as_view(), name='fetch-period'),
    path('fetch-departments/',views.FetchDepartmentsView.as_view(), name='fetch-departments'),

    path('calculate-salaries/',views.CalculateSalariesView.as_view(), name='calculate-salaries'),
    path('detail/<str:salary_uuid>',views.DetailSalariesView.as_view(), name='detail-salaries'),
    path('delete/<str:salary_uuid>',views.DeleteSalariesView.as_view(), name='delete-salaries'),
    path('update/<str:salary_uuid>',views.UpdateSalariesView.as_view(), name='update-salaries'),
    path('add-salary-adjustment/',views.AddSalaryAdjustmentView.as_view(), name='add-salary-adjustment'),

    path('payroll-period',views.PayrollPeriodView.as_view(), name='payroll-periods'),
    path('fetch-payroll-period/',views.ListPayrollPeriodView.as_view(), name='fetch-payroll-periods'),
    path('payroll-period/create/',views.CreatePayrollPeriodView.as_view(), name='create-payroll-periods'),
    path('payroll-period/create/bulk',views.CreatePayrollPeriodBulkView.as_view(), name='create-payroll-periods-bulk'),
    path('payroll-period/detail/<str:period_uuid>',views.DetailPayrollPeriodView.as_view(), name='detail-payroll-periods'),
    path('payroll-period/delete/<str:period_uuid>',views.DeletePayrollPeriodView.as_view(), name='delete-payroll-periods'),
    path('payroll-period/update/<str:period_uuid>',views.UpdatePayrollPeriodView.as_view(), name='update-payroll-periods'),
]
urlpatterns += staticfiles_urlpatterns()
