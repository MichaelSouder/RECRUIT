from sqlalchemy import Column, Integer, ForeignKey, Table
from app.database import Base

# Many-to-many relationship table for user-study access
user_study = Table(
    'user_study',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('study_id', Integer, ForeignKey('studies.id'), primary_key=True)
)


