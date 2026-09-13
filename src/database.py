from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# create test db in memory
DATABASE_URL = "sqlite:///./test.db"

# engine to manage database connections pool
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread":False})

# uses th pool connections to query the db
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# inherits DeclarativeBase so all the Models that inherits Base gets tracked in the metadata
class Base(DeclarativeBase):
    pass

# dependency injection helper for the db
def get_db():
    db = SessionLocal()
    try:
        yield  db
    finally:
        db.close()