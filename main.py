app = FastAPI()
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Memory(BaseModel):
    text: str

memory_store = []

@app.get("/")
def root():
    return {"message": "Memory API is alive!"}

@app.post("/memories")
def add_memory(memory: Memory):
    memory_store.append(memory.text)
    return {"status": "Memory saved!"}

@app.get("/memories")
def get_memories():
    return {"memories": memory_store}
