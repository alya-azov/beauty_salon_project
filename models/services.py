from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

#класс для категорий услуг
class ServiceCategory(Base):
    __tablename__ = 'service_categories'
    
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(100), unique=True, nullable=False)

    services = relationship("Service", back_populates="category")

    def __repr__(self):
        return ("Category()" + self.category_name + ")")

#класс для услуг
class Service(Base):
    __tablename__ = 'services'
    
    service_id = Column(Integer, primary_key=True)
    service_name = Column(String(50), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('service_categories.category_id'))

    category = relationship("ServiceCategory", back_populates="services")

    def __repr__(self):
        #возвращает название, длительность и стоимость услуги
        return ("Услуга(" + self.service_name + " " + str(self.price) + " руб. " + str(self.duration_minutes) + " мин.)")
    
    @property
    def good_format_time(self) -> str:
        # возвращает длительность в формате часов и минут
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60

        if hours > 0: #type: ignore
            return f"{hours} ч {minutes} мин"
        else:
            return f"{minutes} мин"
        

