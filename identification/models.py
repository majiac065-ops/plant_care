from django.db import models
from django.contrib.auth.models import User


class PlantIdentificationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='identifications', null=True, blank=True)
    uploaded_image = models.ImageField(upload_to='plant_uploads/')
    identified_name = models.CharField(max_length=200, default="Pending Identification", blank=True)
    scientific_name = models.CharField(max_length=200, blank=True)
    confidence_score = models.FloatField(default=0.0, help_text="Confidence percentage e.g. 96.5")
    care_summary = models.TextField(blank=True)
    identified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-identified_at']
        verbose_name_plural = "Plant Identification Histories"

    def __str__(self):
        return f"{self.identified_name} ({self.confidence_score}%)"
