from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base, master_service_category

class Master(Base):
    __tablename__ = "masters"

    master_id = Column(Integer, primary_key=True)
    first_name = Column(String(50),nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    specialty = Column(String(100), nullable=False)

    service_categories = relationship("ServiceCategory", secondary=master_service_category, back_populates="masters")
    schedule = relationship("MasterSchedule", back_populates="master", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="master", cascade="all, delete-orphan")

    def __repr__(self):
        return ("Master(" + self.first_name + " " + self.last_name + " - " + self.specialty + ")")

    @property
    # возвращает полное имя мастера
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    


