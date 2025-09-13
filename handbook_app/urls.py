from django.urls import path
from . import views

app_name='handbook'

urlpatterns = [
    # Handbook API
    path('handbooks/', views.ListCreateHandbook.as_view(), name='list_create_handbook'),
    path('handbooks/<int:id>/', views.RetrieveUpdateDestroyHandbook.as_view(), name='retrieve_update_destroy_handbook'),
    # Question API
    path('questions/<slug:company>/', views.AskQuestion.as_view(), name='answer_question')
]
