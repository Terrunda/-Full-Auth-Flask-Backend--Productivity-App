#!/usr/bin/env python3
from app import app
from models import db, User, JournalEntry
from faker import Faker

fake = Faker()

sample_tags = [
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
            new_user = User(
                username=f"user_{i + 1}",
                email=f"user_{i + 1}@example.com",
            )
            new_user.set_password("Password123!")
            db.session.add(new_user)
            users.append(new_user)

        db.session.commit()

        print("Seeding journal entries...")
        for user in users:
            for _ in range(20):
                random_tags = fake.random_elements(
                    sample_tags,
                    length=fake.random_int(min=1, max=4),
                    unique=True,
                )
                tags_string = ",".join(random_tags)
                random_paragraphs = fake.paragraphs(nb=fake.random_int(min=1, max=3))

                new_entry = JournalEntry(
                    title=fake.sentence(nb_words=6).rstrip("."),
                    content="\n\n".join(random_paragraphs),
                    tags=tags_string,
                    user_id=user.id,
                )
                db.session.add(new_entry)

        db.session.commit()

        print("\nDone! Seeded:")
        print(f"  {len(users)} users, 20 journal entries each ({len(users) * 20} total)")
        print("\nCredentials (username / password):")
        for user in users:
            print(f"  {user.username} / Password123!")


if __name__ == "__main__":
    seed()