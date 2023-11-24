from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, Float, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DataStaging(Base):
    __tablename__ = 'data_staging'

    url = Column(String, primary_key=True)
    price = Column(String)
    status = Column(String)
    size = Column(String)
    property_type = Column(String)
    rooms = Column(String)
    floor = Column(String)
    year_built = Column(String)
    property_condition = Column(String)
    location = Column(String)
    desc = Column(String)
    image_url = Column(String)


@dataclass
class DataStagingCols:
    URL: str = 'url'
    PRICE: str = 'price'
    STATUS: str = 'status'
    SIZE: str = 'size'
    PROPERTY_TYPE: str = 'property_type'
    ROOMS: str = 'rooms'
    FLOOR: str = 'floor'
    YEAR_BUILT: str = 'year_built'
    PROPERTY_CONDITION: str = 'property_condition'
    LOCATION: str = 'location'
    DESC: str = 'desc'
    IMAGE_URL = 'image_url'


class DataMain(Base):
    __tablename__ = 'data_main'

    url = Column(String, primary_key=True)
    price = Column(Float)
    status = Column(String(10))
    size = Column(Float)
    property_type = Column(String(10))
    rooms = Column(Integer)
    floor = Column(Integer)
    year_built = Column(Integer)
    property_condition = Column(String(30))
    location = Column(String(30))
    desc = Column(String)
    image_url = Column(String)

    ck_status = CheckConstraint(status.in_(['pierwotny', 'wtórny']))
    ck_size = CheckConstraint(size.between(0, 1000))
    ck_property_type = CheckConstraint(property_type.in_(['dom', 'kamienica', 'blok']))
    ck_rooms = CheckConstraint(rooms.between(0, 20))
    ck_floor = CheckConstraint(floor.between(0, 30))
    ck_year_built = CheckConstraint(year_built.between(1000, 2050))
    ck_property_condition = CheckConstraint(property_condition.in_(['do zamieszkania', 'do wykończenia', 'do remontu']))


@dataclass
class DataMainCols:
    URL: str = 'url'
    PRICE: str = 'price'
    STATUS: str = 'status'
    SIZE: str = 'size'
    PROPERTY_TYPE: str = 'property_type'
    ROOMS: str = 'rooms'
    FLOOR: str = 'floor'
    YEAR_BUILT: str = 'year_built'
    PROPERTY_CONDITION: str = 'property_condition'
    LOCATION: str = 'location'
    DESC: str = 'desc'
    IMAGE_URL = 'image_url'



