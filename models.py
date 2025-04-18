from sqlalchemy import Column, Integer, String, Date
from database import Base

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    tags = Column(String)
    date = Column(String)
