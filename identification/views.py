from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import PlantUploadForm
from .models import PlantIdentificationHistory
from .ml_engine import PlantMLEngine


def identify_plant_view(request):
    if request.method == 'POST':
        form = PlantUploadForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            if request.user.is_authenticated:
                record.user = request.user
            if record.confidence_score is None:
                record.confidence_score = 0.0
            record.save()

            # Execute Image Processing & ML Classification engine
            try:
                result = PlantMLEngine.identify_plant(record.uploaded_image.path)
            except Exception:
                result = {}

            # Update history model record with ML prediction
            record.identified_name = result.get('name', 'Unknown Plant')
            record.scientific_name = result.get('scientific_name', '')

            confidence = result.get('confidence_score')
            if confidence is None:
                confidence = 0.0
            else:
                try:
                    confidence = float(confidence)
                except (ValueError, TypeError):
                    confidence = 0.0

            record.confidence_score = confidence
            record.care_summary = result.get('care_summary', '')
            record.save()

            messages.success(request, f"Plant identified with {record.confidence_score}% confidence!")
            return redirect('identification_result', record_id=record.id)
        else:
            messages.error(request, "Please upload a valid image file.")
    else:
        form = PlantUploadForm()

    history = PlantIdentificationHistory.objects.filter(user=request.user)[:5] if request.user.is_authenticated else []

    context = {
        'form': form,
        'history': history,
        'title': 'Identify Plant - PlantCare'
    }
    return render(request, 'identification/identify.html', context)


def identification_result_view(request, record_id):
    record = get_object_or_404(PlantIdentificationHistory, id=record_id)
    context = {
        'record': record,
        'title': f'Result: {record.identified_name} - PlantCare'
    }
    return render(request, 'identification/result.html', context)
