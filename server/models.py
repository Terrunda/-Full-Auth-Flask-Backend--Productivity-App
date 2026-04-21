from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import MetaData
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