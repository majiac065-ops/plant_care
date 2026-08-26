from django.urls import path
from . import views

urlpatterns = [
    path('', views.care_info_view, name='plant_care_home'),
    path('care-guide/', views.care_info_view, name='care_info'),
    path('save/', views.save_plant_from_care_view, name='save_plant_from_care'),
]
