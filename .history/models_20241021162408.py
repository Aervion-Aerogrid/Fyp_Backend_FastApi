from sqlalchemy import Boolean, Column, Integer, String
from database import Base
from pydantic import BaseModel
class Admin(Base):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, nullable=False)
    password = Column(String(10), nullable=False)

# Pydantic model for data type
class DataTypeRequest(BaseModel):
    datatype: str