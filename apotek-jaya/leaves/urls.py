from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'leaves'
urlpatterns = [
    path('',views.LeavesView.as_view(), name='leaves'),
    path('fetch-leaves/',views.ListLeavesView.as_view(), name='fetch-leaves'),
    path('create/',views.CreateLeavesView.as_view(), name='create-leaves'),
    path('detail/<str:leave_uuid>',views.DetailLeavesView.as_view(), name='detail-leaves'),
    path('delete/<str:leave_uuid>',views.DeleteLeavesView.as_view(), name='delete-leaves'),
    path('update/<str:leave_uuid>',views.UpdateLeavesView.as_view(), name='update-leaves'),
    
    path('balance/',views.LeavesBalancesView.as_view(), name='leaves-balances'),
    path('balance/add-leaves-balances/',views.AddLeavesBalancesView.as_view(), name='add-leaves-balances'),
    path('balance/fetch-leaves-balances/',views.ListLeavesBalancesView.as_view(), name='fetch-leaves-balances'),
    path('balance/create/',views.CreateLeavesBalancesView.as_view(), name='create-leaves-balances'),
    path('balance/detail/<str:leave_balance_uuid>',views.DetailLeavesBalancesView.as_view(), name='detail-leaves-balances'),
    path('balance/delete/<str:leave_balance_uuid>',views.DeleteLeavesBalancesView.as_view(), name='delete-leaves-balances'),
    path('balance/update/<str:leave_balance_uuid>',views.UpdateLeavesBalancesView.as_view(), name='update-leaves-balances'),
]
urlpatterns += staticfiles_urlpatterns()
