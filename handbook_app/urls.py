from django.urls import path
from . import views

urlpatterns = [
    path('handbooks/', views.ListCreateHandbook.as_view(), name='list_create_handbook'),
    path('handbooks/<int:id>/', views.RetrieveUpdateDestroyHandbook.as_view(), name='retrieve_update_destroy_handbook')
]
