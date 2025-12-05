from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Table, ForeignKey

Base = declarative_base()


# Связующая таблица для мастеров и категорий услуг
master_service_category = Table('master_service_category',
    Base.metadata,
    Column('master_id', Integer, ForeignKey('masters.master_id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('service_categories.category_id'), primary_key=True)
)