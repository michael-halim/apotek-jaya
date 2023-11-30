from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'main_app'
urlpatterns = [
    path('login/',views.LoginPageView.as_view(), name='login'),
    path('logout/',views.logoutPage, name='logout'),
]
urlpatterns += staticfiles_urlpatterns()
