from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import os

# Load env variable for DB URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Set up SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define DB model
class MemoryDB(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Define API app
app = FastAPI()

# Pydantic schemas
class MemoryCreate(BaseModel):
    text: str

class MemoryResponse(BaseModel):
    id: int
    text: str
    created_at: datetime

    class Config:
        orm_mode = True

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/")
def root():
    return {"message": "Memory API is alive with DB!"}

@app.post("/memories", response_model=MemoryResponse)
def add_memory(memory: MemoryCreate, db: Session = Depends(get_db)):
    db_memory = MemoryDB(text=memory.text)
    db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    return db_memory

@app.get("/memories", response_model=list[MemoryResponse])
def get_memories(db: Session = Depends(get_db)):
    return db.query(MemoryDB).order_by(MemoryDB.created_at.desc()).all()

@app.put("/memories/{memory_id}", response_model=MemoryResponse)
def update_memory(memory_id: int, updated_memory: MemoryCreate, db: Session = Depends(get_db)):
    memory = db.query(MemoryDB).filter(MemoryDB.id == memory_id).first()
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found.")

    memory.text = updated_memory.text
    db.commit()
    db.refresh(memory)
    return memory
    
@app.delete("/memories/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    memory = db.query(MemoryDB).filter(MemoryDB.id == memory_id).first()
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found.")

    db.delete(memory)
    db.commit()
    return {"message": f"Memory {memory_id} deleted."}
