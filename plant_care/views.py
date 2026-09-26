from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .care_api import PlantCareAPIClient
from dashboard.models import SavedPlant
from identification.models import PlantIdentificationHistory


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
            # ചെടി നിലവിൽ സേവ് ചെയ്തിട്ടുണ്ടോ എന്ന് പരിശോധിക്കുന്നു
            existing = SavedPlant.objects.filter(user=request.user, plant_name__iexact=plant_name).first()
            if existing:
                messages.warning(request, f"'{plant_name}' is already in your dashboard collection!")
            else:
                # യൂസർ അപ്‌ലോഡ് ചെയ്ത ഏറ്റവും പുതിയ ഫോട്ടോ കണ്ടുപിടിക്കുന്നു
                latest_identification = PlantIdentificationHistory.objects.filter(
                    user=request.user,
                    identified_name__icontains=plant_name
                ).order_by('-identified_at').first()

                # പേര് വെച്ച് കിട്ടിയില്ലെങ്കിൽ യൂസറുടെ അവസാനത്തെ അപ്‌ലോഡ് റെക്കോർഡ് എടുക്കുന്നു
                if not latest_identification:
                    latest_identification = PlantIdentificationHistory.objects.filter(
                        user=request.user
                    ).order_by('-identified_at').first()

                plant_image = latest_identification.uploaded_image if (latest_identification and latest_identification.uploaded_image) else None

                SavedPlant.objects.create(
                    user=request.user,
                    plant_name=plant_name,
                    scientific_name=scientific_name,
                    watering_frequency=watering,
                    sunlight_requirement=sunlight,
                    soil_type=soil,
                    fertilizer_info=fertilizer,
                    plant_image=plant_image,
                    notes=f"Saved from Plant Care Guide."
                )
                messages.success(request, f"'{plant_name}' has been added to your Dashboard collection!")
            return redirect('dashboard')

    messages.error(request, "Unable to save plant care details.")
    return redirect('care_info')