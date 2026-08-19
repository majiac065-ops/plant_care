from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import SavedPlant
from .forms import SavedPlantForm
from identification.models import PlantIdentificationHistory


def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'dashboard/home.html', {'title': 'PlantCare: A Smart Plant Care System'})


@login_required
def dashboard_view(request):
    query = request.GET.get('q', '')
    plants = SavedPlant.objects.filter(user=request.user)

    if query:
        plants = plants.filter(
            Q(plant_name__icontains=query) |
            Q(scientific_name__icontains=query) |
            Q(notes__icontains=query)
        )

    recent_identifications = PlantIdentificationHistory.objects.filter(user=request.user)[:3]

    context = {
        'plants': plants,
        'query': query,
        'total_plants': SavedPlant.objects.filter(user=request.user).count(),
        'recent_identifications': recent_identifications,
        'title': 'My Garden Dashboard - PlantCare'
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def add_plant_view(request):
    if request.method == 'POST':
        form = SavedPlantForm(request.POST, request.FILES)
        if form.is_valid():
            plant = form.save(commit=False)
            plant.user = request.user
            plant.save()
            messages.success(request, f"'{plant.plant_name}' added to your garden collection!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = SavedPlantForm()

    context = {
        'form': form,
        'title': 'Add New Plant - PlantCare'
    }
    return render(request, 'dashboard/edit_plant.html', context)


@login_required
def plant_detail_view(request, plant_id):
    plant = get_object_or_404(SavedPlant, id=plant_id, user=request.user)
    context = {
        'plant': plant,
        'title': f'{plant.plant_name} Details - PlantCare'
    }
    return render(request, 'dashboard/plant_detail.html', context)


@login_required
def edit_plant_view(request, plant_id):
    plant = get_object_or_404(SavedPlant, id=plant_id, user=request.user)
    if request.method == 'POST':
        form = SavedPlantForm(request.POST, request.FILES, instance=plant)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated care details for '{plant.plant_name}'.")
            return redirect('plant_detail', plant_id=plant.id)
        else:
            messages.error(request, "Error saving updates. Please review inputs.")
    else:
        form = SavedPlantForm(instance=plant)

    context = {
        'form': form,
        'plant': plant,
        'title': f'Edit {plant.plant_name} - PlantCare'
    }
    return render(request, 'dashboard/edit_plant.html', context)


@login_required
def delete_plant_view(request, plant_id):
    plant = get_object_or_404(SavedPlant, id=plant_id, user=request.user)
    if request.method == 'POST':
        name = plant.plant_name
        plant.delete()
        messages.success(request, f"Successfully removed '{name}' from your collection.")
        return redirect('dashboard')

    context = {
        'plant': plant,
        'title': f'Confirm Delete {plant.plant_name}'
    }
    return render(request, 'dashboard/confirm_delete.html', context)
