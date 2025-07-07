from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class Property(Base):
    __tablename__ = "properties"

    property_id = Column(Text, primary_key=True)
    avm_property_id = Column(Text)
    street_address = Column(Text)
    city = Column(Text)
    state = Column(Text)
    zip_code = Column(Text)
    county = Column(Text)
    carrier_route = Column(Text)
    lot_area_acres = Column(Float)
    lot_area_sqft = Column(Integer)
    lot_area_usable_sqft = Column(Integer)
    topography_type = Column(Text)
    property_type_code = Column(Text)
    land_use_code = Column(Text)
    state_land_use_code = Column(Text)
    state_land_use_desc = Column(Text)

    coordinates = relationship("Coordinate", back_populates="property", cascade="all, delete-orphan")
    building_summary = relationship("BuildingSummary", uselist=False, back_populates="property")
    building_details = relationship("BuildingDetail", uselist=False, back_populates="property")
    owners = relationship("Owner", back_populates="property")
    tax_assessment = relationship("TaxAssessment", uselist=False, back_populates="property")
    last_market_sale = relationship("LastMarketSale", uselist=False, back_populates="property")
    buyers = relationship("Buyer", back_populates="property")
    sellers = relationship("Seller", back_populates="property")

class Coordinate(Base):
    __tablename__ = "coordinates"

    property_id = Column(Text, ForeignKey("properties.property_id"), primary_key=True)
    coord_type = Column(Text, primary_key=True)  # 'parcel' or 'block'
    lat = Column(Float)
    lng = Column(Float)

    property = relationship("Property", back_populates="coordinates")

class BuildingSummary(Base):
    __tablename__ = "building_summary"

    property_id = Column(Text, ForeignKey("properties.property_id"), primary_key=True)
    buildings_count = Column(Integer)
    bathrooms_count = Column(Integer)
    full_bathrooms_count = Column(Integer)
    half_bathrooms_count = Column(Integer)
    bathroom_fixtures_count = Column(Integer)
    fireplaces_count = Column(Integer)
    living_area_sqft = Column(Integer)
    total_area_sqft = Column(Integer)

    property = relationship("Property", back_populates="building_summary")

class BuildingDetail(Base):
    __tablename__ = "building_details"

    property_id = Column(Text, ForeignKey("properties.property_id"), primary_key=True)
    stories_count = Column(Integer)
    year_built = Column(Integer)
    effective_year_built = Column(Integer)
    building_quality_type_code = Column(Text)
    frame_type_code = Column(Text)
    foundation_type_code = Column(Text)
    building_improvement_condition_code = Column(Text)
    patios_count = Column(Integer)
    patios_area_sqft = Column(Integer)
    porches_count = Column(Integer)
    porches_area_sqft = Column(Integer)
    pool_area_sqft = Column(Integer)
    walls_type_code = Column(Text)
    roof_type_code = Column(Text)
    roof_cover_type_code = Column(Text)

    property = relationship("Property", back_populates="building_details")

class Owner(Base):
    __tablename__ = "owners"

    owner_id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Text, ForeignKey("properties.property_id"))
    sequence_number = Column(Integer)
    full_name = Column(Text)
    first_name = Column(Text)
    middle_name = Column(Text)
    last_name = Column(Text)
    is_corporate = Column(Boolean)

    property = relationship("Property", back_populates="owners")

class TaxAssessment(Base):
    __tablename__ = "tax_assessment"

    property_id = Column(Text, ForeignKey("properties.property_id"), primary_key=True)
    year = Column(Integer)
    total_tax_amount = Column(Float)
    county_tax_amount = Column(Float)
    total_assessed_value = Column(Float)
    land_value = Column(Float)
    improvement_value = Column(Float)
    improvement_value_percentage = Column(Integer)
    last_assessor_update_date = Column(Text)
    certification_date = Column(Text)
    school_district_code = Column(Text)
    school_district_name = Column(Text)

    property = relationship("Property", back_populates="tax_assessment")

class LastMarketSale(Base):
    __tablename__ = "last_market_sale"

    property_id = Column(Text, ForeignKey("properties.property_id"), primary_key=True)
    sale_date = Column(Text)
    recording_date = Column(Text)
    amount = Column(Float)
    document_type_code = Column(Text)
    document_number = Column(Text)
    book_number = Column(Text)
    page_number = Column(Text)
    multi_or_split_parcel_code = Column(Text)
    is_mortgage_purchase = Column(Boolean)
    is_resale = Column(Boolean)
    title_company_name = Column(Text)
    title_company_code = Column(Text)

    property = relationship("Property", back_populates="last_market_sale")

class Buyer(Base):
    __tablename__ = "buyers"

    buyer_id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Text, ForeignKey("properties.property_id"))
    full_name = Column(Text)
    last_name = Column(Text)
    first_name_and_middle_initial = Column(Text)

    property = relationship("Property", back_populates="buyers")

class Seller(Base):
    __tablename__ = "sellers"

    seller_id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Text, ForeignKey("properties.property_id"))
    full_name = Column(Text)

    property = relationship("Property", back_populates="sellers")
