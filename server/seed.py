#!/usr/bin/env python3
from app import app
from datetime import date

from models import db, User, JournalEntry
from faker import Faker

fake = Faker()

fake = Faker()
 
SAMPLE_TAGS = [
    "work", "personal", "goals", "reflection", "gratitude",
    "ideas", "health", "family", "travel", "learning",
]
 
 
def seed():
    with app.app_context():
        print("Clearing existing data...")
        JournalEntry.query.delete()
        User.query.delete()
        db.session.commit()
 
        print("Seeding users...")
        users = []
        for i in range(3):
            user = User(username=f"user_{i + 1}")
            user.set_password("Password123!")
            db.session.add(user)
            users.append(user)
 
        db.session.commit()
 
        print("Seeding journal entries...")
        for user in users:
            for _ in range(20):
                tags = fake.random_elements(
                    SAMPLE_TAGS,
                    length=fake.random_int(min=1, max=4),
                    unique=True,
                )
                entry = JournalEntry(
                    title=fake.sentence(nb_words=6).strip("."),
                    content="\n\n".join(fake.paragraphs(nb=fake.random_int(min=1, max=3))),
                    tags=",".join(tags),
                    user_id=user.id,
                )
                db.session.add(entry)
 
        db.session.commit()
 
 
 
if __name__ == "__main__":
    seed()
