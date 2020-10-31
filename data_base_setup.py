from sqlalchemy import Column, ForeignKey, Integer, String, Float, create_engine   # noqa:D100
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class hotels(Base):
    __tablename__ = 'hotels'
    hotel_id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    score = Column(String(4), nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String(100), nullable=False)
    link = Column(String(100), nullable=False)


class coordinates(hotels):
    __tablename__ = 'coordinates'
    hotel_id = Column(Integer, ForeignKey('hotels.hotel_id'), primary_key=True)
    latitude = Column(String(100), nullable=False)
    longitude = Column(String(100), nullable=False)


class important_facilities(hotels):
    __tablename__ = 'important_facilities'
    hotel_id = Column(Integer, ForeignKey('hotels.hotel_id'), primary_key=True)
    important_facilities = Column(String(100), nullable=False)


class neighborhood_structures(hotels):
    __tablename__ = 'neighborhood_structures'
    neighborhood_structures_id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.hotel_id'))
    neighborhood_structures = Column(String(100), nullable=True)


class services_offered(hotels):
    __tablename__ = 'services_offered'
    services_offered_id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.hotel_id'))
    services_offered = Column(String(100), nullable=False)
    value = Column(String(1000), nullable=False)


DBEngine = create_engine('sqlite:///hotels.db', echo=False)
Base.metadata.create_all(DBEngine)
