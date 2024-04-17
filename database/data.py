from sqlalchemy.orm import declarative_base
from sqlalchemy import Column
from sqlalchemy import String, Float, Date, PickleType

Base = declarative_base()


class Station(Base):
    __tablename__ = "Station"
    station = Column(String, primary_key=True, nullable=False)
    name = Column(String, primary_key=True, nullable=False)
    uic_code = Column(String, primary_key=True, nullable=True)
    transport_network = Column(String, primary_key=True, nullable=True)
    address = Column(String, primary_key=False, nullable=True)
    # address = Column(String, primary_key=True, nullable=True)
    type = Column(String, primary_key=True, nullable=True)
    # connecting_line = Column(String, primary_key=False, nullable=True)
    connecting_line = Column(String, primary_key=True, nullable=True)
    opening_date = Column(Date, primary_key=True, nullable=True)
    geo_latitude = Column(Float, primary_key=True, nullable=False)
    geo_longitude = Column(Float, primary_key=True, nullable=False)


    def __repr__(self):
        return (
            f"Station: ("
            f" station: {self.station}, name: {self.name},"
            f" uic_code: {self.uic_code if not None else ""},"
            f" transport_network: {self.transport_network if not None else ""},"
            f" address: {self.address if not None else ""},"
            f" type: {self.type if not None else ""},"
            f" connecting_line: {self.connecting_line if not None else ""},"
            f" opening_date: {self.opening_date if not None else ""},"
            f" geo_latitude: {self.geo_latitude if not None else ""},"
            f" geo_longitude {self.geo_longitude if not None else ""})"
        )

    def convert_to_dict(self):
        return {
            "station": self.station, "name": self.name, "uic_code": self.uic_code, "transport_network": self.transport_network, "address": self.address, "type": self.type, "connecting_line": self.connecting_line, "opening_date": self.opening_date, "geo_latitude": self.geo_latitude, "geo_longitude": self.geo_longitude
        }