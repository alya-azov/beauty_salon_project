from sqlalchemy import Column, String, DateTime, Float, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from datetime import datetime
import enum

Base = declarative_base()

class DiscountLevel(enum.Enum):
    STANDARD = "STANDARD"
    SILVER = "SILVER" 
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"

class SalonCard(Base):
    __tablename__ = "salon_cards"
    
    client_id = Column(Integer, ForeignKey('clients.client_id'), primary_key=True)
    discount_level = Column(Enum(DiscountLevel), default=DiscountLevel.STANDARD, nullable=False)
    total_spent = Column(Float, default=0.0, nullable=False)
    issue_date = Column(DateTime, default=datetime.now, nullable=False)
    
    client = relationship("Client", back_populates="salon_card")
    
    def __repr__(self):
        return "SalonCard (client_id=" + str(self.client_id) + " level=" + self.discount_level.value + " spent=" + str(self.total_spent) + ")"
    
    #повысить уровень карты, при достижении нужной суммы
    def upgrade_level(self):
        if self.total_spent >= 30000 and self.discount_level != DiscountLevel.PLATINUM: #type: ignore
            self.discount_level = DiscountLevel.PLATINUM
        elif self.total_spent >= 15000 and self.discount_level not in [DiscountLevel.PLATINUM, DiscountLevel.GOLD]:#type: ignore
            self.discount_level = DiscountLevel.GOLD
        elif self.total_spent >= 5000 and self.discount_level == DiscountLevel.STANDARD:#type: ignore
            self.discount_level = DiscountLevel.SILVER
    
    #применение скидки к сумме
    def apply_discount(self, amount: float) -> float:
        discount_rates = {
            DiscountLevel.STANDARD: 0.0,
            DiscountLevel.SILVER: 0.03,
            DiscountLevel.GOLD: 0.07,
            DiscountLevel.PLATINUM: 0.10
        }
        
        discount = amount * discount_rates[self.discount_level] # type: ignore
        return amount - discount

class Client(Base):
    __tablename__ = "clients"
    
    client_id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False, unique=True)
    email = Column(String(100), unique=True)
    password_hash = Column(String(255), nullable=False)
    
    salon_card = relationship("SalonCard", back_populates="client", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Client({self.first_name} {self.last_name} - {self.email})"
    
    @property
    def full_name(self) -> str:
        return str(self.first_name) + " " +  str(self.last_name)
    