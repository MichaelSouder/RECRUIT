from sqlalchemy import Column, Integer, ForeignKey, Table
from app.database import Base

# Many-to-many relationship table
subject_study = Table(
    'subject_study',
    Base.metadata,
    Column('subject_id', Integer, ForeignKey('subjects.id'), primary_key=True),
    Column('study_id', Integer, ForeignKey('studies.id'), primary_key=True)
)


