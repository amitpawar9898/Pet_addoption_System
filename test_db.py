from app import create_app, db, Pet, PETS

def test_database():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if we already have pets
        existing_pets = Pet.query.all()
        if not existing_pets:
            print("Adding sample pets to database...")
            # Add sample pets from PETS list
            for pet_data in PETS:
                pet = Pet(
                    name=pet_data['name'],
                    species=pet_data['species'],
                    breed=pet_data['breed'],
                    age_years=pet_data['age_years'],
                    sex=pet_data['sex'],
                    size=pet_data['size'],
                    description=pet_data['description'],
                    photo_url=pet_data['photo_url'],
                    status=pet_data['status'],
                    traits=pet_data['traits']
                )
                db.session.add(pet)
            
            # Commit the changes
            db.session.commit()
            print("Sample pets added successfully!")
        else:
            print(f"Found {len(existing_pets)} existing pets in database")
            
        # Test query
        print("\nQuerying available pets:")
        available_pets = Pet.query.filter_by(status='available').all()
        for pet in available_pets:
            print(f"- {pet.name} ({pet.species})")

if __name__ == "__main__":
    test_database()