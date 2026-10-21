from sqlalchemy import Column, DateTime, Integer, String, func

from src.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())