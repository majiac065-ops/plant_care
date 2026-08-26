from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .care_api import PlantCareAPIClient
from dashboard.models import SavedPlant


def care_info_view(request):
    query = request.GET.get('q', 'Monstera')
    care_data = PlantCareAPIClient.get_care_info(query)
    
    context = {
        'query': query,
        'care_data': care_data,
        'title': f'Care Guide: {care_data["name"]} - PlantCare'
    }
    return render(request, 'plant_care/care_info.html', context)


@login_required
def save_plant_from_care_view(request):
    if request.method == 'POST':
        plant_name = request.POST.get('plant_name')
        scientific_name = request.POST.get('scientific_name', '')
        watering = request.POST.get('watering', '')
        sunlight = request.POST.get('sunlight', '')
        soil = request.POST.get('soil', '')
        fertilizer = request.POST.get('fertilizer', '')

        if plant_name:
            # Check if plant already saved
            existing = SavedPlant.objects.filter(user=request.user, plant_name__iexact=plant_name).first()
            if existing:
                messages.warning(request, f"'{plant_name}' is already in your dashboard collection!")
            else:
                SavedPlant.objects.create(
                    user=request.user,
                    plant_name=plant_name,
                    scientific_name=scientific_name,
                    watering_frequency=watering,
                    sunlight_requirement=sunlight,
                    soil_type=soil,
                    fertilizer_info=fertilizer,
                    notes=f"Saved from Plant Care Guide."
                )
                messages.success(request, f"'{plant_name}' has been added to your Dashboard collection!")
            return redirect('dashboard')

    messages.error(request, "Unable to save plant care details.")
    return redirect('care_info')
