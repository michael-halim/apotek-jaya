from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'departments'
urlpatterns = [
    path('',views.DepartmentsView.as_view(), name='departments'),
    path('fetch-departments/',views.ListDepartmentsView.as_view(), name='fetch-departments'),
    path('create/',views.CreateDepartmentsView.as_view(), name='create-departments'),
    path('add-employees/',views.AddEmployeeDepartmentsView.as_view(), name='add-employee-departments'),
    path('detail/<str:department_uuid>',views.DetailDepartmentsView.as_view(), name='detail-departments'),
    path('delete/<str:department_uuid>',views.DeleteDepartmentsView.as_view(), name='delete-departments'),
    path('update/<str:department_uuid>',views.UpdateDepartmentsView.as_view(), name='update-departments'),
]
urlpatterns += staticfiles_urlpatterns()
