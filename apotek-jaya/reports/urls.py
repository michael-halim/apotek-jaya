from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'reports'
urlpatterns = [
    path('salary',views.ReportsSalaryView.as_view(), name='reports-salary'),
    path('presence',views.ReportsPresenceView.as_view(), name='reports-presence'),
    path('fetch-period/',views.FetchPeriodsView.as_view(), name='fetch-period'),
    path('fetch-departments/',views.FetchDepartmentsView.as_view(), name='fetch-departments'),
    path('fetch-reports-salary/',views.ListReportsSalaryView.as_view(), name='fetch-reports-salary'),
    path('fetch-reports-presence/',views.ListReportsPresenceView.as_view(), name='fetch-reports-presence'),
    
]
urlpatterns += staticfiles_urlpatterns()
