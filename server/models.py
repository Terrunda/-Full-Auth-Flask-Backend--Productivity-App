from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import validates
from sqlalchemy import MetaData
from datetime import datetime

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=True)
    password_hash = db.Column(db.String, nullable=False)
    date_of_creation = db.Column(db.DateTime, default=datetime.today(), nullable=False)

    entries = db.relationship("JournalEntry", back_populates="author")

    def set_password(self, password: str) -> None:
        """Hash and store the user's password using bcrypt."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verify a plain-text password against the stored bcrypt hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    @validates("username")
    def validate_username(self, key, username):
        if not (3 <= len(username) <= 20):
            raise ValueError("Username must be between 3 and 20 characters.")
        return username


class JournalEntry(db.Model):
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    journal_creation_date = db.Column(db.DateTime, default=datetime.today(), nullable=False)

    author = db.relationship("User", back_populates="entries")

    @validates("title")
    def validate_title(self, key, title):
        if not (1 <= len(title) <= 200):
            raise ValueError("Title must be between 1 and 200 characters.")
        return title