from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# 📄 USERS TABLE (Authentication)
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum('Admin', 'User', name='role_enum'),
        nullable=False,
        default='User'
        )

    # One-to-One Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete')
    education = db.relationship('EducationDetail', backref='user', uselist=False, cascade='all, delete')
    language = db.relationship('LanguageSkill', backref='user', uselist=False, cascade='all, delete')


# 👤 USER PROFILES TABLE
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    title = db.Column(db.Enum('Mr', 'Mrs', 'Miss', 'Ms',  name='title_enum'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other', name='gender_enum'), nullable=False)

    # 📞 Contact
    primary_email = db.Column(db.String(255), nullable=False)
    alternative_email = db.Column(db.String(255))
    mobile_number = db.Column(db.String(20), nullable=False)
    home_phone = db.Column(db.String(20))
    emergency_name = db.Column(db.String(100), nullable=False)
    emergency_relationship = db.Column(db.String(50), nullable=False)
    emergency_phone = db.Column(db.String(20), nullable=False)

    # 🌍 Citizenship
    nationality = db.Column(db.String(100), nullable=False)
    country_of_birth = db.Column(db.String(100), nullable=False)
    citizenship_status = db.Column(
        db.Enum('Citizen', 'Permanent Resident', 'International', name='citizenship_enum'),
        nullable=False
    )


# 🗣️ LANGUAGE SKILLS TABLE
class LanguageSkill(db.Model):
    __tablename__ = 'language_skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    english_proficiency = db.Column(db.Enum('Fluent', 'Intermediate', 'Basic', name='english_enum'), nullable=False)
    other_languages = db.Column(db.Text)  # comma-separated values


# 🎓 EDUCATION DETAILS TABLE
class EducationDetail(db.Model):
    __tablename__ = 'education_details'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    secondary_education_level = db.Column(db.String(100), nullable=False)
    highest_completed_level = db.Column(db.String(100), nullable=False)
    still_enrolled = db.Column(db.Boolean, nullable=False)
    previous_qualification = db.Column(
        db.Enum('None', "Bachelor's", "Master's", 'Diploma', name='qualification_enum'),
        nullable=True
    )
