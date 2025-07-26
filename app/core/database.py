from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create engine with better connection pool settings
engine = create_engine(
    settings.DATABASE_URL,
    # Connection pool settings
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,  # Recycle connections every hour
    pool_pre_ping=True,  # Validate connections before use
    connect_args={
        "options": "-c statement_timeout=600000"  # 10 minutes timeout
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            print(f"Error closing database session: {str(e)}")