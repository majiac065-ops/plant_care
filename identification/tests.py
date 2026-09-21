import io
from unittest.mock import patch
from PIL import Image
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import PlantIdentificationHistory


def create_test_image():
    file_obj = io.BytesIO()
    image = Image.new('RGB', size=(100, 100), color=(0, 128, 0))
    image.save(file_obj, 'jpeg')
    file_obj.seek(0)
    return SimpleUploadedFile("test_plant.jpg", file_obj.read(), content_type="image/jpeg")


class PlantIdentificationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_model_default_confidence_score(self):
        """Verify PlantIdentificationHistory model defaults confidence_score to 0.0 without IntegrityError."""
        test_img = create_test_image()
        record = PlantIdentificationHistory.objects.create(uploaded_image=test_img)
        self.assertIsNotNone(record.confidence_score)
        self.assertEqual(record.confidence_score, 0.0)

    def test_identify_plant_view_success(self):
        """Test complete image upload and plant identification flow."""
        test_img = create_test_image()
        response = self.client.post(reverse('identify_plant'), {'uploaded_image': test_img}, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify database record created
        record = PlantIdentificationHistory.objects.last()
        self.assertIsNotNone(record)
        self.assertGreater(record.confidence_score, 0.0)
        self.assertNotEqual(record.identified_name, "Pending Identification")

    @patch('identification.ml_engine.PlantMLEngine.identify_plant')
    def test_identify_plant_view_fallback_when_ml_returns_none(self, mock_identify):
        """Verify that if ML returns confidence_score as None, default value 0.0 is saved."""
        mock_identify.return_value = {
            'name': 'Mystery Plant',
            'scientific_name': 'Unknownus',
            'confidence_score': None,
            'care_summary': 'No info'
        }
        test_img = create_test_image()
        response = self.client.post(reverse('identify_plant'), {'uploaded_image': test_img})
        self.assertEqual(response.status_code, 302)

        record = PlantIdentificationHistory.objects.last()
        self.assertIsNotNone(record)
        self.assertEqual(record.confidence_score, 0.0)
        self.assertEqual(record.identified_name, 'Mystery Plant')

    def test_plant_classes_metadata_loading(self):
        """Verify that 47 supported house plant species are loaded from plant_classes.json."""
        from identification.ml_engine import PlantMLEngine
        classes = PlantMLEngine.get_supported_classes()
        self.assertEqual(len(classes), 47)
        self.assertIn("Monstera Deliciosa", classes)
        self.assertIn("Aloe Vera", classes)
        self.assertIn("Snake Plant", classes)

    def test_low_confidence_threshold_flag(self):
        """Verify that low confidence scores trigger low_confidence flag and warning message."""
        import tempfile
        from identification.ml_engine import PlantMLEngine

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=True) as tmp:
            img = Image.new('RGB', size=(224, 224), color=(100, 100, 100))
            img.save(tmp.name, format='JPEG')

            result = PlantMLEngine.identify_plant(tmp.name)
            self.assertIn('low_confidence', result)
            self.assertIn('supported_classes', result)
            self.assertEqual(len(result['supported_classes']), 47)

    def test_feature_extraction_accuracy(self):
        """Test feature extraction output keys (green_ratio, hue_hist, brightness, aspect_ratio)."""
        import tempfile
        import numpy as np
        from identification.ml_engine import PlantMLEngine

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=True) as tmp:
            img = Image.new('RGB', size=(400, 200), color=(0, 160, 50))
            img.save(tmp.name, format='JPEG')

            specs, rgb_255, rgb_np, hsv_np = PlantMLEngine.preprocess_image(tmp.name)
            features = PlantMLEngine.extract_features(rgb_np, hsv_np, specs=specs)

            self.assertIn('green_ratio', features)
            self.assertIn('hue_hist', features)
            self.assertIn('brightness', features)
            self.assertEqual(len(features['hue_hist']), 8)
            self.assertEqual(features['aspect_ratio'], 2.0)



