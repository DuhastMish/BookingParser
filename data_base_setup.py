from sqlalchemy import (Column, Float, ForeignKey, Integer,  # noqa:D100
                        String, create_engine)
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
    city = Column(String(100), nullable=False)
    open_date = Column(String(100), nullable=True)
    star = Column(Integer, nullable=False)

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
    neighborhood_structure = Column(String(100), nullable=True)
    structure_type = Column(String(1000), nullable=False)
    distance = Column(String(100), nullable=False)


class services_offered(hotels):
    __tablename__ = 'services_offered'
    services_offered_id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.hotel_id'))
    services_offered = Column(String(100), nullable=False)
    value = Column(String(1000), nullable=False)


class extended_rating(hotels):
    __tablename__ = 'extended_rating'
    extended_rating_id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.hotel_id'))
    rating_name = Column(String(100), nullable=False)
    rating_value = Column(Float, nullable=False)


class review_rating(hotels):
    __tablename__ = 'review_rating'
    review_rating_id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.hotel_id'))
    review_rating_name = Column(String(100), nullable=False)
    review_rating_count = Column(Integer, nullable=False)


class apartaments(hotels):
    __tablename__ = 'apartaments'
    apartaments_id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.hotel_id'))
    apartaments_name = Column(String(100), nullable=False)
    apartaments_price = Column(String(100), nullable=False)
    services_offered = Column(String(1000), nullable=True)
    hotel_beds = Column(Integer, nullable=False)


DBEngine = create_engine('sqlite:///hotels.db', echo=False)
Base.metadata.create_all(DBEngine)
