from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import os

# Load env variable for DB URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set. Please set it in your .env file.")

# Set up SQLAlchemy
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define DB model
class MemoryDB(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    tags = Column(String, default="")  # Comma-separated like "#Work,#Health"
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Define API app
app = FastAPI(
    title="Memory API",
    description="An API for storing and retrieving memory entries"
)

# Pydantic schemas
class MemoryCreate(BaseModel):
    text: str
    tags: str = ""  # Default empty string if none

class MemoryResponse(BaseModel):
    id: int
    text: str
    tags: str
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
@app.get("/", response_model=dict)
def root() -> dict:
    return {"message": "Memory API is alive with DB!"}

@app.post("/memories", response_model=MemoryResponse)
def add_memory(memory: MemoryCreate, db: Session = Depends(get_db)) -> MemoryResponse:
    db_memory = MemoryDB(text=memory.text, tags=memory.tags)
    db.add(db_memory)
    try:
        db.commit()
        db.refresh(db_memory)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    return db_memory

@app.get("/memories", response_model=list[MemoryResponse])
def get_memories(tag: str = None, db: Session = Depends(get_db)) -> list[MemoryResponse]:
    query = db.query(MemoryDB)
    if tag:
        query = query.filter(MemoryDB.tags.ilike(f"%{tag}%"))
    return query.order_by(MemoryDB.created_at.desc()).all()

@app.put("/memories/{memory_id}", response_model=MemoryResponse)
def update_memory(memory_id: int, updated_memory: MemoryCreate, db: Session = Depends(get_db)) -> MemoryResponse:
    memory = db.query(MemoryDB).filter(MemoryDB.id == memory_id).first()
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found.")

    memory.text = updated_memory.text
    memory.tags = updated_memory.tags
    try:
        db.commit()
        db.refresh(memory)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    return memory

@app.delete("/memories/{memory_id}", response_model=dict)
def delete_memory(memory_id: int, db: Session = Depends(get_db)) -> dict:
    memory = db.query(MemoryDB).filter(MemoryDB.id == memory_id).first()
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found.")

    try:
        db.delete(memory)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    return {"message": f"Memory {memory_id} deleted."}
