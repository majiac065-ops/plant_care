from django.urls import path
from . import views

urlpatterns = [
    path('', views.identify_plant_view, name='identify_plant'),
    path('result/<int:record_id>/', views.identification_result_view, name='identification_result'),
]
