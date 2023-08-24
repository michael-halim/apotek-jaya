from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'benefits'
urlpatterns = [
    path('scheme/detail/<str:benefit_scheme_uuid>',views.DetailBenefitSchemeView.as_view(), name='detail-benefit-scheme'),
    path('scheme/delete/<str:benefit_scheme_uuid>',views.DeleteBenefitSchemeView.as_view(), name='delete-benefit-scheme'),
    path('scheme/update/<str:benefit_scheme_uuid>',views.UpdateBenefitSchemeView.as_view(), name='update-benefit-scheme'),
    path('scheme/fetch-benefit-scheme/',views.ListBenefitSchemeView.as_view(), name='fetch-benefit-scheme'),
    path('scheme/add-benefit-detail/',views.AddBenefitDetailView.as_view(), name='add-benefit-detail'),
    path('scheme/show-employees-department/',views.ShowEmployeesDepartmentView.as_view(), name='show-employees-department'),
    path('scheme/create/',views.CreateBenefitSchemeView.as_view(), name='create-benefit-scheme'),
    path('scheme',views.BenefitSchemeView.as_view(), name='benefit-scheme'),

    path('category/detail/<str:benefit_category_uuid>',views.DetailBenefitCategoriesView.as_view(), name='detail-benefit-categories'),
    path('category/delete/<str:benefit_category_uuid>',views.DeleteBenefitCategoriesView.as_view(), name='delete-benefit-categories'),
    path('category/update/<str:benefit_category_uuid>',views.UpdateBenefitCategoriesView.as_view(), name='update-benefit-categories'),
    path('category/fetch-benefit-categories/',views.ListBenefitCategoriesView.as_view(), name='fetch-benefit-categories'),
    path('category/create/',views.CreateBenefitCategoriesView.as_view(), name='create-benefit-categories'),
    path('category',views.BenefitCategoriesView.as_view(), name='benefit-categories'),
    
    path('detail/<str:benefit_uuid>',views.DetailBenefitsView.as_view(), name='detail-benefits'),
    path('delete/<str:benefit_uuid>',views.DeleteBenefitsView.as_view(), name='delete-benefits'),
    path('update/<str:benefit_uuid>',views.UpdateBenefitsView.as_view(), name='update-benefits'),
    path('fetch-benefits/',views.ListBenefitsView.as_view(), name='fetch-benefits'),
    path('create/',views.CreateBenefitsView.as_view(), name='create-benefits'),
    path('',views.BenefitsView.as_view(), name='benefits'),

]
urlpatterns += staticfiles_urlpatterns()
