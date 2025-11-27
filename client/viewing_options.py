from models.masters import Master
from sqlalchemy.orm import Session

# вывести всех мастеров (нет не из себя)
def get_all_masters(session: Session) -> None:
    masters = session.query(Master).all()
    for master in masters:
        print(str(master.master_id) + ") " + master.first_name + " " + master.last_name + " " + master.specialty)
    print()


# вывести мастеров по специальности
def get_masters_by_specialty(session: Session, specialty: str) -> None:
    masters = session.query(Master).filter(Master.specialty == specialty).all()
    print("Мастера специальности: " + specialty)
    for master in masters:
        print(str(master.master_id) + ") " + master.first_name + " " + master.last_name)
    print()
