from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import MetaData

from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# Relationship will be a one-to-many where one user can have multiple journals.

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    date_of_creation = db.Column(db.DateTime, default=datetime.today(), nullable=False)
    
    entries = db.relationship("JournalEntry",back_populates="author")

    
    def set_password(self, password: str) -> None:
        """Hash and store the user's password using Werkzeug's pbkdf2 hashing."""
        self.password_hash = generate_password_hash(password)
 
    def check_password(self, password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    @validates("username")
    def validate_username(self, key, username):
        if not (3 <= len(username) <= 80):
            raise ValueError("Username must be between 3 and 80 characters.")
        return username

class JournalEntry(db.Model):
    __tablename__ = "journal_entries"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(500), nullable=True)  
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False) # Foreign key that links to the Users table.
    journal_creation_date = db.Column(db.DateTime, default=datetime.today(), nullable=False)

    #One to many relation.
    author = db.relationship("User", back_populates="entries")

    @validates("title")
    def validate_title(self, key, title):
        if not (1 <= len(title) <= 200):
            raise ValueError("Title must be between 1 and 200 characters.")
        return title