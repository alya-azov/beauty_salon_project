from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Master(Base):
    __tablename__ = "masters"

    master_id = Column(Integer, primary_key=True)
    first_name = Column(String(50),nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    specialty = Column(String(100), nullable=False)

    def __repr__(self):
        return ("Master(" + self.first_name + " " + self.last_name + " - " + self.specialty + ")")

    @property
    # возвращает полное имя мастера
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


