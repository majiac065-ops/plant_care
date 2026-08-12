import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plantcare_project.settings')
django.setup()

from django.contrib.auth.models import User
from dashboard.models import SavedPlant
from accounts.models import UserProfile

def seed():
    print("Seeding initial demo data for PlantCare System...")
    
    # 1. Create Demo Admin User
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@plantcare.com',
            password='admin123',
            first_name='System',
            last_name='Admin'
        )
        print("-> Created Superuser: admin (password: admin123)")
    else:
        admin_user = User.objects.get(username='admin')

    # 2. Create Demo Gardener User
    if not User.objects.filter(username='gardener').exists():
        gardener = User.objects.create_user(
            username='gardener',
            email='gardener@plantcare.com',
            password='gardener123',
            first_name='Green',
            last_name='Thumb'
        )
        gardener.profile.bio = "Passionate indoor botanist & foliage collector."
        gardener.profile.location_zone = "Indoor Balcony / Zone 8b"
        gardener.profile.phone_number = "+1 (555) 321-7890"
        gardener.profile.save()
        print("-> Created Demo User: gardener (password: gardener123)")
    else:
        gardener = User.objects.get(username='gardener')

    # 3. Seed Sample Saved Plants for Demo User
    sample_plants = [
        {
            "plant_name": "Monstera Deliciosa",
            "scientific_name": "Monstera deliciosa",
            "watering_frequency": "Every 7-10 days when top 2 inches of soil feel dry.",
            "sunlight_requirement": "Bright, indirect sunlight near an east or west window.",
            "soil_type": "Rich, well-draining potting mix containing peat moss and perlite.",
            "fertilizer_info": "Balanced 20-20-20 liquid fertilizer monthly during spring/summer.",
            "confidence_score": 96.8,
            "notes": "Repotted in April with fresh perlite blend. New leaf split emerging!"
        },
        {
            "plant_name": "Snake Plant (Sansevieria)",
            "scientific_name": "Dracaena trifasciata",
            "watering_frequency": "Every 2-3 weeks. Drought tolerant.",
            "sunlight_requirement": "Adapts to low, medium, or bright indirect light.",
            "soil_type": "Coarse succulent & cactus soil blend with sand.",
            "fertilizer_info": "Diluted houseplant food once in May.",
            "confidence_score": 98.4,
            "notes": "Placed in home office shelf. Very low maintenance."
        },
        {
            "plant_name": "Fiddle Leaf Fig",
            "scientific_name": "Ficus lyrata",
            "watering_frequency": "Once weekly with filtered lukewarm water.",
            "sunlight_requirement": "Consistent bright direct morning sun.",
            "soil_type": "Peat moss blend with compost for drainage.",
            "fertilizer_info": "High-nitrogen plant food bi-weekly in growing season.",
            "confidence_score": 94.2,
            "notes": "Wipe large leaves with damp microfiber cloth monthly."
        }
    ]

    for data in sample_plants:
        plant, created = SavedPlant.objects.get_or_create(
            user=gardener,
            plant_name=data['plant_name'],
            defaults=data
        )
        if created:
            print(f"-> Added saved plant demo: {data['plant_name']}")

    print("\nDatabase seeding completed successfully!")

if __name__ == '__main__':
    seed()
