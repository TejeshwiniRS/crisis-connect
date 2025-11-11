"""
Populate Firestore 'ngos' collection with verified, factual global NGO data.
Run this once locally (with gcloud auth application-default login) or from a Cloud Run job.
"""

from google.cloud import firestore
import os

def seed_verified_ngos():
    ngos = [
        {"name": "American Red Cross", "service": "medical supplies", "country": "USA", "location": "Washington D.C."},
        {"name": "Feeding America", "service": "food", "country": "USA", "location": "Chicago"},
        {"name": "Habitat for Humanity International", "service": "shelter", "country": "USA", "location": "Atlanta"},
        {"name": "International Rescue Committee", "service": "shelter", "country": "USA", "location": "New York"},
        {"name": "CARE International", "service": "food", "country": "Switzerland", "location": "Geneva"},
        {"name": "Médecins Sans Frontières", "service": "medical supplies", "country": "France", "location": "Paris"},
        {"name": "Action Against Hunger", "service": "food", "country": "France", "location": "Paris"},
        {"name": "Save the Children", "service": "medical supplies", "country": "United Kingdom", "location": "London"},
        {"name": "Oxfam International", "service": "food", "country": "Kenya", "location": "Nairobi"},
        {"name": "World Vision International", "service": "food", "country": "Kenya", "location": "Nairobi"},
        {"name": "Caritas Internationalis", "service": "shelter", "country": "Italy", "location": "Rome"},
        {"name": "Red Cross Society of China", "service": "medical supplies", "country": "China", "location": "Beijing"},
        {"name": "Japan Platform", "service": "shelter", "country": "Japan", "location": "Tokyo"},
        {"name": "BRAC Bangladesh", "service": "food", "country": "Bangladesh", "location": "Dhaka"},
        {"name": "Islamic Relief Worldwide", "service": "shelter", "country": "United Kingdom", "location": "Birmingham"},
        {"name": "Australian Red Cross", "service": "medical supplies", "country": "Australia", "location": "Sydney"},
        {"name": "UNICEF India", "service": "medical supplies", "country": "India", "location": "New Delhi"},
        {"name": "Relief Society of Tigray", "service": "food", "country": "Ethiopia", "location": "Mekelle"},
        {"name": "Red Crescent Society of the UAE", "service": "medical supplies", "country": "United Arab Emirates", "location": "Abu Dhabi"},
        {"name": "Catholic Relief Services", "service": "food", "country": "USA", "location": "Baltimore"},
        {"name": "Mercy Malaysia", "service": "medical supplies", "country": "Malaysia", "location": "Kuala Lumpur"},
        {"name": "Plan International", "service": "shelter", "country": "United Kingdom", "location": "London"},
        {"name": "Norwegian Refugee Council", "service": "shelter", "country": "Norway", "location": "Oslo"},
        {"name": "IFRC", "service": "medical supplies", "country": "Switzerland", "location": "Geneva"},
        {"name": "South African Red Cross Society", "service": "medical supplies", "country": "South Africa", "location": "Pretoria"},
        {"name": "Samaritan’s Purse", "service": "food", "country": "USA", "location": "Boone"},
        {"name": "Tearfund", "service": "shelter", "country": "United Kingdom", "location": "London"},
        {"name": "CARE Australia", "service": "food", "country": "Australia", "location": "Canberra"},
        {"name": "Médecins du Monde", "service": "medical supplies", "country": "France", "location": "Paris"},
        {"name": "Danish Refugee Council", "service": "shelter", "country": "Denmark", "location": "Copenhagen"},
    ]

    db = firestore.Client(database=os.getenv("GOOGLE_CLOUD_FIRESTORE_DB"))
    count = 0
    for ngo in ngos:
        doc_id = f"{ngo['name'].lower().replace(' ', '_')}_{ngo['country'].lower()}"
        db.collection("ngos").document(doc_id).set({
            **ngo,
            "source": "verified_manual_seed",
        })
        count += 1

    print(f"✅ Seeded {count} verified NGOs into Firestore 'ngos' collection.")


if __name__ == "__main__":
    seed_verified_ngos()
