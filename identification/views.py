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

            # Execute Image Preprocessing & ML Classification engine
            try:
                result = PlantMLEngine.identify_plant(record.uploaded_image.path)
            except Exception:
                result = {}

            # Update history model record with ML prediction output
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

            if result.get('low_confidence'):
                messages.warning(request, f"Plant identified as '{record.identified_name}' with low confidence ({record.confidence_score}%). Please check warning details.")
            else:
                messages.success(request, f"Plant identified as '{record.identified_name}' with {record.confidence_score}% confidence!")

            return redirect('identification_result', record_id=record.id)
        else:
            messages.error(request, "Please select a valid plant or leaf image file to upload.")
    else:
        form = PlantUploadForm()

    history = PlantIdentificationHistory.objects.filter(user=request.user)[:5] if request.user.is_authenticated else []
    supported_classes = PlantMLEngine.get_supported_classes()

    context = {
        'form': form,
        'history': history,
        'supported_classes': supported_classes,
        'title': 'Identify Plant - PlantCare'
    }
    return render(request, 'identification/identify.html', context)


def identification_result_view(request, record_id):
    record = get_object_or_404(PlantIdentificationHistory, id=record_id)
    
    metadata = PlantMLEngine.load_metadata()
    species_info = metadata.get("species_info", {})
    matched_meta = species_info.get(record.identified_name, {})
    supported_classes = metadata.get("classes", [])

    # Low confidence thresholding (55%)
    low_confidence = record.confidence_score < 55.0
    warning_message = ""
    if low_confidence:
        warning_message = (
            f"Low confidence prediction ({record.confidence_score}%). The uploaded photo may be blurry, poorly lit, "
            f"or contain a plant species outside our 47 supported house plant classes."
        )

    # Determine confidence badge styling
    if record.confidence_score >= 85:
        badge_style = 'bg-success'
        confidence_level = 'High Confidence Match'
    elif record.confidence_score >= 55:
        badge_style = 'bg-warning text-dark'
        confidence_level = 'Moderate Confidence Match'
    else:
        badge_style = 'bg-danger text-white'
        confidence_level = 'Uncertain / Low Confidence'

    context = {
        'record': record,
        'matched_meta': matched_meta,
        'badge_style': badge_style,
        'confidence_level': confidence_level,
        'low_confidence': low_confidence,
        'warning_message': warning_message,
        'supported_classes': supported_classes,
        'title': f'Result: {record.identified_name} - PlantCare'
    }
    return render(request, 'identification/result.html', context)


