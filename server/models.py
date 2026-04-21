from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import MetaData

import bcrypt
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
    
    # Changed from werkzeug to bcrypt for hashing passwords
    def set_password(self, password: str) -> None:
        byte_password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(byte_password, salt)
        
        self.password_hash = hashed_password.decode('utf-8')

    def check_password(self, password: str) -> bool:
        byte_password = password.encode('utf-8')
        byte_hash = self.password_hash.encode('utf-8')
        
        return bcrypt.checkpw(byte_password, byte_hash)
    
    @validates("username")
    def validate_username(self, key, username):
        if not (3 <= len(username) <= 20):
            raise ValueError("Username must be between 3 and 20 characters.")

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