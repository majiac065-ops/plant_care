from django.db import models
from django.contrib.auth.models import User


class SavedPlant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_plants')
    plant_name = models.CharField(max_length=200)
    scientific_name = models.CharField(max_length=200, blank=True)
    plant_image = models.ImageField(upload_to='saved_plants/', blank=True, null=True)
    watering_frequency = models.TextField(blank=True, help_text="e.g. Every 7 days or when top soil dries")
    sunlight_requirement = models.TextField(blank=True, help_text="e.g. Bright indirect sunlight")
    soil_type = models.TextField(blank=True, help_text="e.g. Well-draining potting mix with perlite")
    fertilizer_info = models.TextField(blank=True, help_text="e.g. Liquid fertilizer every 4 weeks in summer")
    confidence_score = models.FloatField(null=True, blank=True, help_text="Score if saved from identification")
    notes = models.TextField(blank=True, help_text="Personal care notes or reminders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.plant_name} ({self.user.username})"
