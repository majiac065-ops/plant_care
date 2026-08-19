from django import forms
from .models import SavedPlant


class SavedPlantForm(forms.ModelForm):
    class Meta:
        model = SavedPlant
        fields = [
            'plant_name',
            'scientific_name',
            'plant_image',
            'watering_frequency',
            'sunlight_requirement',
            'soil_type',
            'fertilizer_info',
            'notes'
        ]
        widgets = {
            'plant_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Monstera Deliciosa'}),
            'scientific_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Monstera deliciosa'}),
            'plant_image': forms.FileInput(attrs={'class': 'form-control'}),
            'watering_frequency': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Watering schedule details...'}),
            'sunlight_requirement': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Sunlight & light preferences...'}),
            'soil_type': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Soil mixture recommendation...'}),
            'fertilizer_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Fertilizer routines...'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Personal care notes, repotting history...'}),
        }
