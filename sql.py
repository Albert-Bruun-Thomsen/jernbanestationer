from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, update, delete
from datetime import date
from data import Station, Base

from sqlalchemy.engine import Engine
from sqlalchemy import event


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


Database = "sqlite:///data.db"


def create_test_data():
    with Session(engine) as session:
        new_items = []
        new_items.append(Station(
            station="DEF456",
            name="Station B",
            uic_code="UIC456",
            transport_network="Rail",
            address="456 Elm Street",
            type="Terminal",
            connecting_line="Blue Line",
            opening_date=date(1995, 10, 20),
            geo_latitude=34.0522,
            geo_longitude=-118.2437
        ))
        session.add_all(new_items)
        session.commit()
        print("Test data created successfully")


if __name__ == "__main__":  # executed when file is executed directly
    engine = create_engine(Database, echo=False, future=True)
    Base.metadata.create_all(engine)
    create_test_data()

else:
    engine = create_engine(Database, echo=False, future=True)
    Base.metadata.create_all(engine)
