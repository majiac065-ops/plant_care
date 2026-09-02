from django import forms
from .models import PlantIdentificationHistory


class PlantUploadForm(forms.ModelForm):
    class Meta:
        model = PlantIdentificationHistory
        fields = ["uploaded_image"]

        widgets = {
            "uploaded_image": forms.FileInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "accept": "image/*",
                    "id": "plantImageInput",
                }
            )
        }
