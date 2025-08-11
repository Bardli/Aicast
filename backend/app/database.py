from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# For this initial setup, we use SQLite.
# The architectural document specifies PostgreSQL, which can be configured later.
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args is needed only for SQLite to allow multithreading.
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a DB session.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
