from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'benefits'
urlpatterns = [
    path('',views.BenefitsView.as_view(), name='benefits'),
    path('fetch-benefits/',views.ListBenefitsView.as_view(), name='fetch-benefits'),
    path('create/',views.CreateBenefitsView.as_view(), name='create-benefits'),
    # path('add-employees/',views.AddEmployeeBenefitsView.as_view(), name='add-employee-benefits'),
    path('detail/<str:benefit_uuid>',views.DetailBenefitsView.as_view(), name='detail-benefits'),
    path('delete/<str:benefit_uuid>',views.DeleteBenefitsView.as_view(), name='delete-benefits'),
    path('update/<str:benefit_uuid>',views.UpdateBenefitsView.as_view(), name='update-benefits'),
]
urlpatterns += staticfiles_urlpatterns()
