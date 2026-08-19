from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('plant/add/', views.add_plant_view, name='add_plant'),
    path('plant/<int:plant_id>/', views.plant_detail_view, name='plant_detail'),
    path('plant/<int:plant_id>/edit/', views.edit_plant_view, name='edit_plant'),
    path('plant/<int:plant_id>/delete/', views.delete_plant_view, name='delete_plant'),
]
