# PlantCare 🌿

PlantCare is an intelligent plant identification and care management platform built with Python, Django, and machine learning computer vision capabilities. It allows users to upload photos of plants for automated species identification, track personal plant collections, receive personalized care guides (watering, sunlight, soil), and manage custom reminder schedules.

## Features

- **Automated Plant Species Identification**: Upload plant images for real-time visual species detection and health assessment.
- **Personalized Care Guides**: Access detailed watering intervals, sunlight requirements, temperature ranges, and soil recommendations.
- **Plant Collection Dashboard**: Save plants to a personal collection, upload custom photos, and track growth progress.
- **Custom Care Schedules**: Receive dynamic watering and care reminders based on plant species requirements.
- **User Authentication**: Secure user registration, authentication, and profile management.

## Tech Stack

- **Backend**: Python 3.14+, Django 5.x
- **Frontend**: HTML5, Modern Vanilla CSS3, Responsive Design
- **ML / Vision Engine**: Custom vision pipeline and feature classification algorithms
- **Database**: SQLite / PostgreSQL
- **Media Storage**: Django File Storage system

## Getting Started

### Prerequisites

- Python 3.10+
- pip & virtualenv

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/majiac065-ops/plant_care.git
   cd plant_care
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Environment Setup:
   ```bash
   cp .env.example .env
   ```

5. Run Database Migrations:
   ```bash
   python manage.py migrate
   ```

6. Load Initial Seed Data (Optional):
   ```bash
   python manage.py shell < seed_data.py
   ```

7. Start the Development Server:
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000/` in your browser.

## Project Structure

```
plant_care/
├── accounts/          # User authentication and profile management
├── dashboard/         # Plant collection dashboard & tracking views
├── identification/    # Vision ML engine & plant species detection module
├── plant_care/        # Care guide database & schedule API logic
├── plantcare_project/ # Django project settings & URL routing
├── templates/         # UI layout templates and components
└── static/            # CSS styles, assets, and static files
```

## Running Tests

Execute the unit test suite:
```bash
python manage.py test
```

## License

MIT License.
