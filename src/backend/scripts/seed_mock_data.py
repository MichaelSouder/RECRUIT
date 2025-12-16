"""
Script to seed the database with comprehensive mock data for testing
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, timedelta, datetime
import random
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.subject import Subject
from app.models.study import Study
from app.models.session_note import SessionNote
from app.models.assessment import Assessment
from app.models.assessment_type import AssessmentType
from app.models.subject_study import subject_study
from app.models.user_study import user_study
from app.core.security import get_password_hash

# Import all models to ensure they're registered
from app.models import User, Subject, Study, SessionNote, Assessment, AssessmentType

# Create all tables
Base.metadata.create_all(bind=engine)

# Mock data
FIRST_NAMES = [
    "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Jessica",
    "William", "Ashley", "James", "Amanda", "Christopher", "Melissa", "Daniel",
    "Nicole", "Matthew", "Michelle", "Anthony", "Kimberly", "Mark", "Amy",
    "Donald", "Angela", "Steven", "Lisa", "Paul", "Nancy", "Andrew", "Karen",
    "Joshua", "Betty", "Kenneth", "Helen", "Kevin", "Sandra", "Brian", "Donna",
    "George", "Carol", "Edward", "Ruth", "Ronald", "Sharon", "Timothy", "Michelle",
    "Jason", "Laura", "Jeffrey", "Sarah", "Ryan", "Kimberly", "Jacob", "Deborah"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
    "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker",
    "Gonzalez", "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner"
]

RACES = ["White", "Black or African American", "Asian", "Native American", "Pacific Islander", "Other", "Hispanic or Latino"]
SEXES = ["male", "female"]

STUDY_NAMES = [
    "Cognitive Recovery Study",
    "Sleep Quality Assessment",
    "Vision Rehabilitation Trial",
    "Balance Improvement Program",
    "Memory Enhancement Research",
    "Anxiety Treatment Study",
    "Depression Intervention Trial",
    "Traumatic Brain Injury Recovery",
    "Post-Stroke Rehabilitation",
    "Chronic Pain Management Study"
]

COUNTIES = [
    "Fairfax County", "Montgomery County", "Prince George's County", "Arlington County",
    "Loudoun County", "Howard County", "Anne Arundel County", "Baltimore County",
    "Chesterfield County", "Henrico County", "Norfolk County", "Richmond County"
]

SESSION_NOTE_TEMPLATES = [
    "Patient showed improvement in cognitive function during today's session.",
    "Discussed treatment progress and addressed patient concerns.",
    "Administered assessment battery. Patient was cooperative throughout.",
    "Follow-up session. Patient reported positive response to intervention.",
    "Initial assessment completed. Baseline measurements recorded.",
    "Patient demonstrated good engagement with therapy exercises.",
    "Reviewed previous session notes and updated treatment plan.",
    "Patient expressed some concerns about progress. Provided reassurance and adjusted approach.",
    "Standard protocol followed. No adverse events reported.",
    "Patient completed all scheduled assessments without difficulty."
]

ASSESSMENT_NOTES = [
    "Assessment completed successfully.",
    "Patient was cooperative and engaged throughout.",
    "Some difficulty noted with certain tasks.",
    "Results consistent with previous assessments.",
    "Notable improvement from baseline.",
    "Standard administration protocol followed."
]


def create_mock_users(db: Session):
    """Create mock users"""
    users = []
    
    # Create admin user
    admin = User(
        email="admin@recruit.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Dr. Sarah Johnson",
        is_active=True,
        is_superuser=True,
        role="admin"
    )
    db.add(admin)
    users.append(admin)
    
    # Create researcher users
    researcher_names = [
        ("researcher1@recruit.com", "Dr. Michael Chen"),
        ("researcher2@recruit.com", "Dr. Emily Rodriguez"),
    ]
    
    for email, full_name in researcher_names:
        user = User(
            email=email,
            hashed_password=get_password_hash("password123"),
            full_name=full_name,
            is_active=True,
            is_superuser=False,
            role="researcher"
        )
        db.add(user)
        users.append(user)
    
    # Create viewer users
    viewer_names = [
        ("viewer1@recruit.com", "Dr. James Wilson"),
        ("viewer2@recruit.com", "Nurse Patricia Martinez"),
        ("viewer3@recruit.com", "Research Coordinator David Lee")
    ]
    
    for email, full_name in viewer_names:
        user = User(
            email=email,
            hashed_password=get_password_hash("password123"),
            full_name=full_name,
            is_active=True,
            is_superuser=False,
            role="viewer"
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"Created {len(users)} users")
    return users


def create_mock_studies(db: Session):
    """Create mock studies with detailed descriptions"""
    studies = []
    
    study_descriptions = {
        "Cognitive Recovery Study": "A comprehensive study examining cognitive recovery patterns in patients with traumatic brain injury. Includes neuropsychological assessments and follow-up evaluations.",
        "Sleep Quality Assessment": "Longitudinal study tracking sleep quality and patterns in patients with sleep disorders. Uses standardized sleep questionnaires.",
        "Vision Rehabilitation Trial": "Clinical trial evaluating vision rehabilitation techniques for patients with acquired vision loss. Includes visual acuity and contrast sensitivity testing.",
        "Balance Improvement Program": "Intervention study focusing on balance and coordination improvements in elderly patients. Includes balance board assessments.",
        "Memory Enhancement Research": "Research study investigating memory enhancement techniques and their effectiveness in patients with mild cognitive impairment.",
        "Anxiety Treatment Study": "Clinical trial evaluating anxiety treatment interventions. Includes psychological assessments and self-report measures.",
        "Depression Intervention Trial": "Multi-site trial examining depression intervention strategies. Uses standardized depression and anxiety scales.",
        "Traumatic Brain Injury Recovery": "Longitudinal study tracking recovery outcomes in TBI patients. Comprehensive assessment battery.",
        "Post-Stroke Rehabilitation": "Clinical study evaluating post-stroke rehabilitation interventions. Includes cognitive and motor assessments.",
        "Chronic Pain Management Study": "Research study examining chronic pain management strategies and their impact on quality of life."
    }
    
    for i, name in enumerate(STUDY_NAMES):
        start_date = date.today() - timedelta(days=random.randint(30, 730))
        end_date = start_date + timedelta(days=random.randint(180, 1095))
        
        study = Study(
            name=name,
            description=study_descriptions.get(name, f"Description for {name}"),
            start_date=start_date,
            end_date=end_date if random.random() > 0.2 else None,
            status=random.choice(["active", "active", "active", "completed", "paused"])
        )
        db.add(study)
        studies.append(study)
    
    db.commit()
    print(f"Created {len(studies)} studies")
    return studies


def create_mock_subjects(db: Session, users: list[User]):
    """Create mock subjects with realistic data"""
    subjects = []
    
    for i in range(150):  # Increased to 150 subjects
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        middle_name = random.choice(FIRST_NAMES) if random.random() > 0.7 else None
        
        # Generate date of birth (between 18 and 85 years ago)
        years_ago = random.randint(18, 85)
        dob = date.today() - timedelta(days=years_ago * 365 + random.randint(0, 365))
        
        # Generate SSN (mock format)
        ssn = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
        
        # Some subjects may have passed away (5% chance)
        death_date = None
        if random.random() < 0.05:
            death_date = dob + timedelta(days=random.randint(18*365, 85*365))
            if death_date > date.today():
                death_date = None
        
        subject = Subject(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            date_of_birth=dob,
            sex=random.choice(SEXES),
            ssn=ssn if random.random() > 0.15 else None,  # 15% don't have SSN
            race=random.choice(RACES),
            death_date=death_date,
            county=random.choice(COUNTIES) if random.random() > 0.2 else None,
            zip=f"{random.randint(10000, 99999)}",
            created_by=random.choice(users).id
        )
        db.add(subject)
        subjects.append(subject)
    
    db.commit()
    print(f"Created {len(subjects)} subjects")
    return subjects


def create_mock_session_notes(db: Session, subjects: list[Subject], studies: list[Study], users: list[User]):
    """Create session notes for subjects"""
    session_notes = []
    
    # Create 2-5 session notes per subject (on average)
    for subject in subjects:
        num_sessions = random.randint(2, 8)
        base_date = date.today() - timedelta(days=random.randint(30, 365))
        
        # Get subject's studies
        subject_studies = [s for s in studies if subject in s.subjects] if hasattr(subject, 'studies') else []
        if not subject_studies:
            # If no studies, randomly assign one
            subject_studies = random.sample(studies, min(1, len(studies)))
        
        for i in range(num_sessions):
            session_date = base_date + timedelta(days=i * random.randint(7, 30))
            if session_date > date.today():
                break
            
            # Assign to a random study from subject's studies
            study = random.choice(subject_studies) if subject_studies else None
                
            note = SessionNote(
                subject_id=subject.id,
                study_id=study.id if study else None,
                session_date=session_date,
                notes=random.choice(SESSION_NOTE_TEMPLATES) + f" Session {i+1} of {num_sessions}.",
                created_by=random.choice(users).id
            )
            db.add(note)
            session_notes.append(note)
    
    db.commit()
    print(f"Created {len(session_notes)} session notes")
    return session_notes


def create_mock_assessments(db: Session, subjects: list[Subject], studies: list[Study], users: list[User]):
    """Create various types of assessments"""
    assessments = []
    
    assessment_types = {
        'moca': {'name': 'MoCA', 'min_score': 0, 'max_score': 30, 'description': 'Montreal Cognitive Assessment'},
        'nihcog': {'name': 'NIH Toolbox', 'min_score': 0, 'max_score': 100, 'description': 'NIH Toolbox Cognitive Battery'},
        'dass21': {'name': 'DASS-21', 'min_score': 0, 'max_score': 42, 'description': 'Depression Anxiety Stress Scales'},
        'pssqi': {'name': 'PSSQI', 'min_score': 0, 'max_score': 21, 'description': 'Pittsburgh Sleep Quality Index'},
        'vision': {'name': 'Vision Acuity', 'min_score': 0, 'max_score': 20, 'description': 'Visual Acuity Assessment'},
        'balance': {'name': 'Balance Test', 'min_score': 0, 'max_score': 100, 'description': 'Balance Assessment'}
    }
    
    # Create assessments for 80% of subjects
    subjects_with_assessments = random.sample(subjects, int(len(subjects) * 0.8))
    
    for subject in subjects_with_assessments:
        # Get subject's studies
        subject_studies = [s for s in studies if subject in s.subjects] if hasattr(subject, 'studies') else []
        if not subject_studies:
            subject_studies = random.sample(studies, min(1, len(studies)))
        
        # Each subject gets 1-4 different types of assessments
        num_assessment_types = random.randint(1, 4)
        selected_types = random.sample(list(assessment_types.keys()), num_assessment_types)
        
        for assessment_type in selected_types:
            # Create 1-3 assessments of each type (longitudinal data)
            num_assessments = random.randint(1, 3)
            base_date = date.today() - timedelta(days=random.randint(60, 365))
            
            for i in range(num_assessments):
                assessment_date = base_date + timedelta(days=i * random.randint(30, 90))
                if assessment_date > date.today():
                    break
                
                type_info = assessment_types[assessment_type]
                score_range = type_info['max_score'] - type_info['min_score']
                # Generate realistic scores (slightly weighted toward middle range)
                base_score = random.uniform(type_info['min_score'], type_info['max_score'])
                # Add some variation for longitudinal data
                if i > 0:
                    base_score += random.uniform(-5, 5)  # Some improvement or decline
                total_score = max(type_info['min_score'], min(type_info['max_score'], base_score))
                
                # Assign to a random study from subject's studies
                study = random.choice(subject_studies) if subject_studies else None
                
                assessment = Assessment(
                    subject_id=subject.id,
                    study_id=study.id if study else None,
                    assessment_type=assessment_type,
                    assessment_date=assessment_date,
                    total_score=round(total_score, 2),
                    notes=random.choice(ASSESSMENT_NOTES),
                    created_by=random.choice(users).id
                )
                db.add(assessment)
                assessments.append(assessment)
    
    db.commit()
    print(f"Created {len(assessments)} assessments")
    print(f"  - MoCA: {sum(1 for a in assessments if a.assessment_type == 'moca')}")
    print(f"  - NIH Cog: {sum(1 for a in assessments if a.assessment_type == 'nihcog')}")
    print(f"  - DASS-21: {sum(1 for a in assessments if a.assessment_type == 'dass21')}")
    print(f"  - PSSQI: {sum(1 for a in assessments if a.assessment_type == 'pssqi')}")
    print(f"  - Vision: {sum(1 for a in assessments if a.assessment_type == 'vision')}")
    print(f"  - Balance: {sum(1 for a in assessments if a.assessment_type == 'balance')}")
    return assessments


def main():
    """Main function to seed all mock data"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Seeding comprehensive mock data...")
        print("=" * 60)
        
        # Clear existing data
        print("\nClearing existing data...")
        db.query(Assessment).delete()
        db.query(SessionNote).delete()
        # Clear association tables
        db.execute(text("DELETE FROM subject_study"))
        db.execute(text("DELETE FROM user_study"))
        db.query(Subject).delete()
        db.query(Study).delete()
        db.query(User).delete()
        db.commit()
        print("✓ Existing data cleared")
        
        users = create_mock_users(db)
        studies = create_mock_studies(db)
        
        # Assign Principal Investigators to studies
        print("\nAssigning Principal Investigators to studies...")
        researchers = [u for u in users if u.role in ["researcher", "admin"]]
        for study in studies:
            if researchers:
                study.principal_investigator_id = random.choice(researchers).id
        db.commit()
        print(f"✓ Assigned PIs to {len(studies)} studies")
        
        subjects = create_mock_subjects(db, users)
        
        # Associate subjects with studies (many-to-many)
        print("\nAssociating subjects with studies...")
        for subject in subjects:
            # Each subject is in 1-3 studies
            num_studies = random.randint(1, min(3, len(studies)))
            selected_studies = random.sample(studies, num_studies)
            # Clear existing and add new to avoid duplicates
            subject.studies.clear()
            subject.studies.extend(selected_studies)
        db.commit()
        print(f"✓ Associated subjects with studies")
        
        # Associate users with studies (for access control)
        print("\nAssociating users with studies...")
        # Clear all existing associations first
        db.execute(text("DELETE FROM user_study"))
        # Admin has access to all studies
        users[0].accessible_studies.clear()
        users[0].accessible_studies.extend(studies)
        # Researchers and viewers get access to 2-5 random studies
        for user in users[1:]:
            user.accessible_studies.clear()
            num_studies = random.randint(2, min(5, len(studies)))
            selected_studies = random.sample(studies, num_studies)
            user.accessible_studies.extend(selected_studies)
        db.commit()
        print(f"✓ Associated users with studies")
        
        session_notes = create_mock_session_notes(db, subjects, studies, users)
        assessments = create_mock_assessments(db, subjects, studies, users)
        
        print("=" * 60)
        print("Mock data seeding completed!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  Users: {len(users)}")
        print(f"  Studies: {len(studies)}")
        print(f"  Subjects: {len(subjects)}")
        print(f"  Session Notes: {len(session_notes)}")
        print(f"  Assessments: {len(assessments)}")
        print(f"\nTest credentials:")
        print(f"  Admin: admin@recruit.com / admin123")
        print(f"  User:  researcher1@recruit.com / password123")
        print(f"\nAverage data per subject:")
        print(f"  Session Notes: {len(session_notes) / len(subjects):.1f}")
        print(f"  Assessments: {len(assessments) / len(subjects):.1f}")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
