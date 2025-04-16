from fastapi import FastAPI, HTTPException
@app.get("/")
def root():
    return {"message": "Memory API is alive!"}
from pydantic import BaseModel
import json
import uuid
from typing import List

app = FastAPI()

DATA_FILE = "memories.json"

class Memory(BaseModel):
    id: str
    title: str
    content: str

def load_memories():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_memories(memories):
    with open(DATA_FILE, "w") as f:
        json.dump(memories, f, indent=2)

@app.get("/memories", response_model=List[Memory])
def get_memories():
    return load_memories()

@app.post("/memories", response_model=Memory)
def add_memory(memory: Memory):
    memories = load_memories()
    memories.append(memory.dict())
    save_memories(memories)
    return memory

@app.put("/memories/{memory_id}", response_model=Memory)
def update_memory(memory_id: str, updated: Memory):
    memories = load_memories()
    for i, mem in enumerate(memories):
        if mem["id"] == memory_id:
            memories[i] = updated.dict()
            save_memories(memories)
            return updated
    raise HTTPException(status_code=404, detail="Memory not found")

@app.delete("/memories/{memory_id}")
def delete_memory(memory_id: str):
    memories = load_memories()
    memories = [m for m in memories if m["id"] != memory_id]
    save_memories(memories)
    return {"detail": "Deleted"}
