import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()
#здесь создадим классы

class hotels(Base):
    _tablename_ = 'HOTELS'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    score = Column(String(4), nullable=False)
    image = Column(String(100), nullable=False)
    link = Column(String(100), nullable=False)

class details(hotels):
    _tablename_ = 'details'

class coordinates(details):    
    _tablename_ = 'coordinates'

    latitude = Column(String(100), nullable = False)
    longitude = Column(String(100), nullable = False)

class important_facilities(details):
    _tablename_ = 'important_facilities'

    important_facilities= Column(String(100), nullable = False)

class neighborhood_structures(details):
    _tablename_ = 'neighborhood_structures'
    neighborhood_structures = Column(String(100), nullable = True)

class services_offered(details):
    _tablename_ = 'services_offered'
class type(services_offered):
    _tablename_ = 'type'
    services_offered = Column(String(100), nullable = False)

class value(services_offered):
    _tablename_ = 'value'
    value = Column(String(100), nullable = False)
    



engine = create_engine('Y-%m-%d-%H.%M.%S')
Base.metadata.create_all(engine)
