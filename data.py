from sqlalchemy.orm import declarative_base
from sqlalchemy import Column
from sqlalchemy import String, Float, Date, PickleType

Base = declarative_base()


class Station(Base):
    __tablename__ = "stations"
    station = Column(String, primary_key=True, nullable=False)
    name = Column(String, primary_key=True, nullable=False)
    uic_code = Column(String)
    transport_network = Column(String)
    address = Column(String)
    type = Column(String)
    connecting_line = Column(String)
    opening_date = Column(Date)
    geo_latitude = Column(Float)
    geo_longitude = Column(Float)

    def __repr__(self):
        print(f"Station: station: {self.station}, name: {self.name}, uic_code: {self.uic_code},"
              f" transport_network: {self.transport_network}, address: {self.address}, type: {self.type},"
              f" connecting_line: {self.connecting_line}, opening_date: {self.opening_date}, geo_latitude:"
              f" {self.geo_latitude}, geo_longitude {self.geo_longitude}")

