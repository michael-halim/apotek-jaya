from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views
from employees.views import EmployeesView

app_name = 'main_app'
urlpatterns = [
    path('',views.HomeView.as_view(), name='home'),
    path('login/',views.loginPage, name='login'),
    path('upload/',views.FileFieldFormView.as_view(), name='upload'),
    path('logout/',views.logoutPage, name='logout'),
]
urlpatterns += staticfiles_urlpatterns()
