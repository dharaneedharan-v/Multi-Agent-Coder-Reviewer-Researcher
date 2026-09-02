
import enum
import uuid as uuid_lib

from sqlalchemy import (
    Boolean, Column, Enum, Integer, Numeric,Float,
    String, ForeignKey, func, DateTime
)
from sqlalchemy.orm import relationship
from src.repositories.database import Base
                                                   
# Error Log                                                   

class Error(Base):

    __tablename__ = "error_log"

    error_id      = Column(Integer, primary_key=True, autoincrement=True)
    file_name     = Column(String,        nullable=False)
    function_name = Column(String,        nullable=False)
    message       = Column(String,        nullable=False)
    error_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    uuid          = Column(String(100), unique=True, nullable=False,default=lambda: str(uuid_lib.uuid4()))
    is_active     = Column(Boolean, default=True)
    created_by    = Column(String,   nullable=True , default="SYSTEM" )
    created_at    = Column(DateTime, server_default=func.now())
    updated_by    = Column(String,   nullable=True , default="SYSTEM" )
    updated_at    = Column(DateTime, server_default=func.now(), onupdate=func.now())                            
                                   
# Customer                                           

class Customer(Base):

    __tablename__ = "customer"

    customer_id      = Column(Integer, primary_key=True, autoincrement=True)
    customer_name    = Column(String,  nullable=False)
    customer_phone   = Column(String,  nullable=False, unique=True)
    customer_address = Column(String,  nullable=False)
    customer_email   = Column(String,  nullable=False, unique=True)

    uuid             = Column(String(100), unique=True, nullable=False,default=lambda: str(uuid_lib.uuid4()))
    is_active        = Column(Boolean, default=True)
    created_by       = Column(String,   nullable=True , default="SYSTEM" )
    created_at       = Column(DateTime, server_default=func.now())
    updated_by       = Column(String,   nullable=True , default="SYSTEM" )
    updated_at       = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # # Relationships
    # orders  = relationship("Order",   back_populates="customer")
    # ratings = relationship("Ratings", back_populates="customer")