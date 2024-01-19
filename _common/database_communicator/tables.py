from dataclasses import dataclass

from sqlalchemy import DATE, JSON, CheckConstraint, Column, Float, Integer, String, Sequence, ForeignKey, TEXT
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DataStaging(Base):
    __tablename__ = "data_staging"

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
    URL: str = "url"
    PRICE: str = "price"
    STATUS: str = "status"
    SIZE: str = "size"
    PROPERTY_TYPE: str = "property_type"
    ROOMS: str = "rooms"
    FLOOR: str = "floor"
    YEAR_BUILT: str = "year_built"
    PROPERTY_CONDITION: str = "property_condition"
    LOCATION: str = "location"
    DESC: str = "desc"
    IMAGE_URL = "image_url"


class DataMain(Base):
    __tablename__ = "data_main"

    url = Column(String, primary_key=True)
    price = Column(Float)
    currency = Column(String(10))
    status = Column(String(30))
    size = Column(Float)
    property_type = Column(String(30))
    rooms = Column(Integer)
    floor = Column(Integer)
    year_built = Column(Integer)
    property_condition = Column(String(30))
    location = Column(String(30))
    desc = Column(String)
    image_url = Column(String)
    insert_date = Column(DATE)
    last_time_seen = Column(DATE)
    row_hash = Column(String(64))
    run_id = Column(String)

    ck_status = CheckConstraint(status.in_(["pierwotny", "wtórny"]))
    ck_property_type = CheckConstraint(
        property_type.in_(["dom", "kamienica", "blok", "apartamentowiec", "inne"])
    )
    ck_property_condition = CheckConstraint(
        property_condition.in_(
            [
                "do zamieszkania",
                "do wykończenia",
                "do remontu",
                "stan surowy zamknięty",
                "stan surowy otwarty",
            ]
        )
    )


@dataclass
class DataMainCols:
    URL: str = "url"
    PRICE: str = "price"
    CURRENCY: str = "currency"
    STATUS: str = "status"
    SIZE: str = "size"
    PROPERTY_TYPE: str = "property_type"
    ROOMS: str = "rooms"
    FLOOR: str = "floor"
    YEAR_BUILT: str = "year_built"
    PROPERTY_CONDITION: str = "property_condition"
    LOCATION: str = "location"
    DESC: str = "desc"
    IMAGE_URL: str = "image_url"
    INSERT_DATE: str = "insert_date"
    LAST_TIME_SEEN: str = "last_time_seen"
    ROW_HASH: str = "row_hash"
    RUN_ID: str = "run_id"


class Models(Base):
    __tablename__ = "models"

    id = Column(Integer, Sequence('models_id_seq'), primary_key=True)
    model_name = Column(String(50))
    model_date = Column(DATE)
    model_mae = Column(Float)
    model_rmse = Column(Float)
    model_r2 = Column(Float)
    model_binary = Column(BYTEA)
    hparams = Column(JSON, nullable=True)


@dataclass
class ModelsCols:
    ID: str = "id"
    MODEL_NAME: str = "model_name"
    MODEL_DATE: str = "model_date"
    MODEL_MAE: str = "model_mae"
    MODEL_RMSE: str = "model_rmse"
    MODEL_R2: str = "model_r2"
    MODEL_BINARY: str = "model_binary"
    HPARAMS: str = 'hparams'


class Opportunities(Base):
    __tablename__ = "opportunities"

    url = Column(String, ForeignKey('data_main.url', ondelete='CASCADE'), primary_key=True)
    predicted_price = Column(Float)
    potential_gain = Column(Float)


@dataclass
class OpportunitiesCols:
    URL: str = "url"
    PREDICTED_PRICE: str = "predicted_price"
    POTENTIAL_GAIN: str = "potential_gain"


class BargainletterEmails(Base):
    __tablename__ = 'bargainletter_emails'

    id = Column(Integer, primary_key=True)
    email = Column(TEXT, nullable=False)
    max_real_price = Column(Float)
    min_potential_gain = Column(Float)
    location = Column(String(30))


@dataclass
class BargainletterEmailsCols:
    ID: str = 'id'
    EMAIL: str = 'email'
    MAX_REAL_PRICE: str = 'max_real_price'
    MIN_POTENTIAL_GAIN: str = 'min_potential_gain'
    LOCATION: str = 'location'
