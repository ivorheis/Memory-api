from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://memory_db_usl6_user:qsbXVOMYpBGpsDE054SCUBG83WhdcYgr@dpg-cvvmt8euk2gs73dfkccg-a.oregon-postgres.render.com/memory_db_usl6"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
