
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.schedule import Appointment, AppointmentStatus
from models.services import Service
from models.masters import Master
from models.clients import Client

def get_test_data():
    """Получаем тестовые данные"""
    session = create_test_database()
    
    # Копируем логику из dashboard.py
    from models.schedule import Appointment
    from models.services import Service
    from models.masters import Master
    from models.clients import Client
    
    appointments = (session.query(
        Appointment,
        Service.service_name,
        Master.first_name,
        Master.last_name,
        Client.first_name.label('client_first_name'),
        Client.last_name.label('client_last_name')
    )
    .join(Service, Appointment.service_id == Service.service_id)
    .join(Master, Appointment.master_id == Master.master_id)
    .join(Client, Appointment.client_id == Client.client_id)
    .all())
    
    data = []
    for app, service_name, master_first, master_last, client_first, client_last in appointments:
        data.append({
            'date': app.start_datetime.date(),
            'service': service_name,
            'master': f"{master_first} {master_last}",
            'client': f"{client_first} {client_last}",
            'price': app.service.price,
            'status': app.status.value,
            'duration': app.service.duration_minutes if app.service else 0
        })
    
    df = pd.DataFrame(data)
    session.close()
    
    return df

def create_test_database():
    """Создаем тестовую БД с данными"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()
    
    service1 = Service(service_name="Стрижка", duration_minutes=60, price=1000, category_id=1)
    
    service2 = Service(service_name="Маникюр", duration_minutes=90, price=1500, category_id=1)
    
    session.add(service1)
    session.add(service2)
    session.flush()
    
    # Создаем тестовых мастеров
    master1 = Master(first_name="Анна", last_name="Иванова", phone="+79111111111", email="anna@test.ru", specialty="Парикмахер")
    
    master2 = Master(first_name="Борис", last_name="Сидоров", phone="+79222222222", email="boris@test.ru", specialty="Мастер маникюра")
    
    session.add(master1)
    session.add(master2)
    session.flush()
    
    # Создаем тестовых клиентов
    client1 = Client(first_name="Иван", last_name="Петров", phone="+79333333333", email="ivan@test.ru", password_hash="hash123")
    
    client2 = Client(first_name="Мария", last_name="Сидорова", phone="+79444444444", email="maria@test.ru", password_hash="hash456")
    
    session.add(client1)
    session.add(client2)
    session.flush()
    
    # Создаем тестовые записи
    appointments = [
        Appointment(master_id=master1.master_id, client_id=client1.client_id, service_id=service1.service_id, schedule_id=1, 
                    start_datetime=datetime(2024, 12, 5, 10, 0), end_datetime=datetime(2024, 12, 5, 11, 0),status=AppointmentStatus.COMPLETED,
                    notes="Тестовая запись 1"),
        Appointment( master_id=master2.master_id, client_id=client2.client_id, service_id=service2.service_id, schedule_id=1,
                    start_datetime=datetime(2024, 12, 8, 14, 0), end_datetime=datetime(2024, 12, 8, 15, 30), status=AppointmentStatus.COMPLETED,
                    notes="Тестовая запись 2"),
        Appointment(master_id=master1.master_id, client_id=client1.client_id, service_id=service1.service_id, schedule_id=1,
                    start_datetime=datetime(2024, 12, 10, 11, 0), end_datetime=datetime(2024, 12, 10, 12, 0), status=AppointmentStatus.CANCELLED,
                    notes="Тестовая запись 3"),
        Appointment(master_id=master2.master_id, client_id=client2.client_id, service_id=service2.service_id, schedule_id=1,
                    start_datetime=datetime(2024, 12, 12, 16, 0), end_datetime=datetime(2024, 12, 12, 17, 30), status=AppointmentStatus.SCHEDULED,
                    notes="Тестовая запись 4")
    ]
    
    for appointment in appointments:
        session.add(appointment)
    
    session.commit()
    
    return session

def test_get_statistics_data():
    """Тест загрузки данных"""
    
    session = create_test_database()
    
    from models.schedule import Appointment
    from models.services import Service
    from models.masters import Master
    from models.clients import Client
    
    appointments = (session.query(
        Appointment,
        Service.service_name,
        Master.first_name,
        Master.last_name,
        Client.first_name.label('client_first_name'),
        Client.last_name.label('client_last_name')
    )
    .join(Service, Appointment.service_id == Service.service_id)
    .join(Master, Appointment.master_id == Master.master_id)
    .join(Client, Appointment.client_id == Client.client_id)
    .all())
    
    data = []
    for app, service_name, master_first, master_last, client_first, client_last in appointments:
        data.append({
            'date': app.start_datetime.date(),
            'service': service_name,
            'master': f"{master_first} {master_last}",
            'client': f"{client_first} {client_last}",
            'price': app.service.price,
            'status': app.status.value,
            'duration': app.service.duration_minutes if app.service else 0
        })
    
    df = pd.DataFrame(data)
    
    assert len(df) == 4
    expected_columns = ['date', 'service', 'master', 'client', 'price', 'status', 'duration']
    for col in expected_columns:
        assert col in df.columns
    
    assert df['price'].sum() == 5000
    
    session.close()
    print("test_get_statistics_data")
    return df


def test_filter_data_by_period():
    """Тест фильтрации по периоду"""
    
    df = get_test_data()
    today = date(2024, 12, 12)
    
    cutoff_date = today - timedelta(days=7)
    df_filtered = df[(df['date'] >= cutoff_date) & (df['date'] <= today)]
    assert len(df_filtered) == 4
    
    cutoff_date = today - timedelta(days=3)
    df_filtered = df[(df['date'] >= cutoff_date) & (df['date'] <= today)]
    assert len(df_filtered) == 2
    
    print("test_filter_data_by_period")

def test_revenue_calculation():
    """Тест расчета доходов"""
    
    df = get_test_data()
    revenue_data = df[df['status'] == 'COMPLETED']
    total_revenue = revenue_data['price'].sum()
    
    assert total_revenue == 2500 
    assert len(revenue_data) == 2
    
    print("test_revenue_calculation")

def test_service_popularity():
    """Тест популярности услуг"""
    
    df = get_test_data()
    service_counts = df['service'].value_counts()
    
    assert len(service_counts) == 2
    assert 'Стрижка' in service_counts.index
    assert 'Маникюр' in service_counts.index
    assert service_counts['Стрижка'] == 2
    assert service_counts['Маникюр'] == 2
    
    print("test_service_popularity")


def test_master_statistics():
    """Тест статистики мастеров"""
    
    df = get_test_data()
    master_stats = df.groupby('master').agg({
        'price': 'sum',
        'service': 'count'
    }).reset_index()
    
    master_stats.columns = ['master', 'revenue', 'appointments']
    
    assert len(master_stats) == 2
    assert 'Анна Иванова' in master_stats['master'].values
    assert 'Борис Сидоров' in master_stats['master'].values
    
    anna_stats = master_stats[master_stats['master'] == 'Анна Иванова'].iloc[0]
    boris_stats = master_stats[master_stats['master'] == 'Борис Сидоров'].iloc[0]
    
    assert anna_stats['revenue'] == 2000
    assert anna_stats['appointments'] == 2
    assert boris_stats['revenue'] == 3000
    assert boris_stats['appointments'] == 2
    
    print("test_master_statistics")

def test_empty_database():
    """Тест с пустой БД"""
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()
    
    from models.schedule import Appointment
    from models.services import Service
    from models.masters import Master
    from models.clients import Client
    
    appointments = (session.query(
        Appointment,
        Service.service_name,
        Master.first_name,
        Master.last_name,
        Client.first_name.label('client_first_name'),
        Client.last_name.label('client_last_name')
    )
    .join(Service, Appointment.service_id == Service.service_id)
    .join(Master, Appointment.master_id == Master.master_id)
    .join(Client, Appointment.client_id == Client.client_id)
    .all())
    
    data = []
    for app, service_name, master_first, master_last, client_first, client_last in appointments:
        data.append({
            'date': app.start_datetime.date(),
            'service': service_name,
            'master': f"{master_first} {master_last}",
            'client': f"{client_first} {client_last}",
            'price': app.service.price,
            'status': app.status.value,
            'duration': app.service.duration_minutes if app.service else 0
        })
    
    df = pd.DataFrame(data)
    
    if df.empty:
        df = pd.DataFrame(columns=['date', 'service', 'master', 'client', 'price', 'status', 'duration'])
    
    assert df.empty
    assert len(df.columns) == 7
    
    session.close()
    print("test_empty_database")


def run_all_tests():
    """Запуск всех тестов"""
    
    df = test_get_statistics_data()
    test_filter_data_by_period()
    test_revenue_calculation()
    test_service_popularity()
    test_master_statistics()
    test_empty_database()
    
    print("\nВСЕ ТЕСТЫ ПРОЙДЕНЫ!")


if __name__ == "__main__":
    run_all_tests()