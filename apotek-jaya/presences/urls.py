from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'presences'
urlpatterns = [
    path('',views.PresencesView.as_view(), name='presences'),
    path('fetch-presences/',views.ListPresencesView.as_view(), name='fetch-presences'),
    path('create/',views.CreatePresencesView.as_view(), name='create-presences'),
    path('create/bulk',views.CreatePresencesBulkView.as_view(), name='create-presences-bulk'),
    path('detail/<str:presence_uuid>',views.DetailPresencesView.as_view(), name='detail-presences'),
    path('delete/<str:presence_uuid>',views.DeletePresencesView.as_view(), name='delete-presences'),
    path('update/<str:presence_uuid>',views.UpdatePresencesView.as_view(), name='update-presences'),
]
urlpatterns += staticfiles_urlpatterns()
