from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import declarative_base, sessionmaker

# Подключение к PostgreSQL
engine = create_engine("postgresql://postgres:4321wwee@localhost:5432/salon_project")
Base = declarative_base()
Session = sessionmaker(engine)
session = Session()

class Service(Base):
    __tablename__ = 'services'
    
    service_id = Column(Integer, primary_key=True)
    service_name = Column(String(50))
    duration_minutes = Column(String(50))
    price = Column(String(20))
    category = Column(String(100))

    def __repr__(self):
        return "Master(" + self.first_name + " " + self.last_name + " - " + self.specialty + ")"