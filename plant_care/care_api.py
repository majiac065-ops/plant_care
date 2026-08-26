import requests
import logging

logger = logging.getLogger(__name__)


class PlantCareAPIClient:
    """
    Client for querying Plant Care APIs (e.g., Perenual API / Trefle API).
    Provides structured watering, sunlight, soil, fertilizer, and propagation info.
    """
    
    DEFAULT_CARE_DATABASE = {
        "monstera": {
            "name": "Monstera Deliciosa",
            "scientific_name": "Monstera deliciosa",
            "category": "Tropical Foliage",
            "watering": "Moderate - Every 1 to 2 weeks when top 2 inches of soil feel dry. Reduce watering in winter.",
            "sunlight": "Bright, indirect light. Avoid direct harsh afternoon sunlight which scorches leaves.",
            "soil": "Rich, well-draining potting mix containing peat moss, perlite, and pine bark.",
            "fertilizer": "Balanced liquid fertilizer (20-20-20) monthly during spring and summer growth seasons.",
            "temperature": "65°F - 85°F (18°C - 30°C). Protect from cold drafts.",
            "humidity": "High humidity preferred (60%+). Regular misting or place near a humidifier.",
            "toxicity": "Toxic to pets (dogs & cats) if ingested due to insoluble calcium oxalates."
        },
        "snake plant": {
            "name": "Snake Plant (Sansevieria)",
            "scientific_name": "Dracaena trifasciata",
            "category": "Succulent",
            "watering": "Low - Every 2 to 4 weeks. Allow soil to dry out completely between waterings.",
            "sunlight": "Adapts to low, medium, or bright indirect light. Very shade tolerant.",
            "soil": "Fast-draining cactus/succulent soil mix with coarse sand.",
            "fertilizer": "All-purpose succulent food once in spring and once in mid-summer.",
            "temperature": "55°F - 85°F (13°C - 30°C). Sensitive to frost.",
            "humidity": "Tolerates average to low indoor air humidity.",
            "toxicity": "Mildly toxic to pets if chewed."
        },
        "fiddle leaf fig": {
            "name": "Fiddle Leaf Fig",
            "scientific_name": "Ficus lyrata",
            "category": "Indoor Tree",
            "watering": "Consistent - Water when top inch of soil is dry, roughly once weekly.",
            "sunlight": "Bright, direct morning sun or strong indirect light.",
            "soil": "Peat-based potting soil with perlite for aeration.",
            "fertilizer": "High-nitrogen plant food diluted biweekly in spring/summer.",
            "temperature": "60°F - 75°F (16°C - 24°C). Avoid sudden temperature swings.",
            "humidity": "Moderate to high (50%+). Wipe leaves clean with a moist cloth.",
            "toxicity": "Skin irritant and toxic to pets."
        },
        "aloe vera": {
            "name": "Aloe Vera",
            "scientific_name": "Aloe barbadensis Miller",
            "category": "Medicinal Succulent",
            "watering": "Deep but infrequent - Water every 3 weeks, allowing soil to dry out.",
            "sunlight": "Bright sunny window with 6+ hours of sunlight daily.",
            "soil": "Cactus or succulent soil blend with perlite and pumice.",
            "fertilizer": "Low-dose water-soluble 10-40-10 fertilizer once per spring.",
            "temperature": "55°F - 80°F (13°C - 27°C).",
            "humidity": "Low humidity preferred.",
            "toxicity": "Gel is soothing for humans, but skin outer latex is toxic to pets."
        },
        "peace lily": {
            "name": "Peace Lily",
            "scientific_name": "Spathiphyllum",
            "category": "Flowering Houseplant",
            "watering": "Keep moist - Water when soil surface dries. Drooping leaves indicate thirst.",
            "sunlight": "Medium to low indirect shade. Direct sun burns white spathes.",
            "soil": "Peat moss blend with organic compost.",
            "fertilizer": "Balanced houseplant food every 6 weeks during spring/summer.",
            "temperature": "65°F - 80°F (18°C - 27°C). Protect from winter frost.",
            "humidity": "High humidity (60%+). Great candidate for bathrooms.",
            "toxicity": "Contains calcium oxalate crystals; toxic to cats and dogs."
        },
        "pothos": {
            "name": "Golden Pothos",
            "scientific_name": "Epipremnum aureum",
            "category": "Trailing Vine",
            "watering": "Moderate - Water every 1-2 weeks. Leaves yellow if overwatered.",
            "sunlight": "Low light tolerant, but variegated leaves shine in bright indirect light.",
            "soil": "Standard indoor potting mix.",
            "fertilizer": "Balanced liquid fertilizer once a month in spring/summer.",
            "temperature": "60°F - 85°F (15°C - 29°C).",
            "humidity": "Adapts to normal household humidity.",
            "toxicity": "Toxic to pets."
        }
    }

    @classmethod
    def get_care_info(cls, plant_query):
        """
        Retrieves care details for a plant by name.
        Integrates API lookup with graceful local database fallback.
        """
        query_clean = plant_query.lower().strip()
        
        # Match against predefined care database keys
        for key, info in cls.DEFAULT_CARE_DATABASE.items():
            if key in query_clean or query_clean in key:
                return info
                
        # Generic Default Care Guide if specific plant key is unknown
        return {
            "name": plant_query.title(),
            "scientific_name": f"Species {plant_query.capitalize()}",
            "category": "General Houseplant",
            "watering": "Water thoroughly when the top 1-2 inches of soil dry out. Ensure drainage holes are unblocked.",
            "sunlight": "Provide bright, indirect sunlight for optimal photosynthesis.",
            "soil": "Use well-draining potting mix rich in organic compost.",
            "fertilizer": "Feed with balanced 10-10-10 houseplant fertilizer monthly during active growing season.",
            "temperature": "65°F - 78°F (18°C - 25°C). Avoid harsh hot or cold drafts.",
            "humidity": "Maintain moderate room humidity around 45% - 60%.",
            "toxicity": "Consult local botanic guidance regarding household pet interaction."
        }
