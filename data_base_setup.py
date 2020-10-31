
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class hotels(Base):
    _tablename_ = 'HOTELS'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    score = Column(String(4), nullable=False)
    image = Column(String(100), nullable=False)
    link = Column(String(100), nullable=False)


class details(hotels):
    _tablename_ = 'details'
    details_id = Column(Integer, ForeignKey('hotels.hotels_id'))


class coordinates(details):
    _tablename_ = 'coordinates'
    coordinates_id = Column(Integer, ForeignKey('details.details_id'))

    latitude = Column(String(100), nullable=False)
    longitude = Column(String(100), nullable=False)


class important_facilities(details):
    _tablename_ = 'important_facilities'
    important_facilities_id = Column(Integer, ForeignKey('details.details_id'))

    important_facilities = Column(String(100), nullable=False)


class neighborhood_structures(details):
    _tablename_ = 'neighborhood_structures'
    neighborhood_structures_id = Column(Integer, ForeignKey('details.details_id'))
    neighborhood_structures = Column(String(100), nullable=True)


class services_offered(details):
    _tablename_ = 'services_offered'
    services_offered_id = Column(Integer, ForeignKey('details.details_id'))
    services_offered = Column(String(100), nullable=False)
    value = Column(String(1000), nullable=False)


engine = create_engine('sqlite:///hotels.db', echo=True)
Base.metadata.create_all(engine)
