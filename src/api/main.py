from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.services.post_service import generate_post

app = FastAPI()

# Allow CORS for all origins (for development; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to your frontend's URL
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    length: str
    language: str
    tag: str

class GenerateResponse(BaseModel):
    response: str

@app.post("/generate", response_model=GenerateResponse)
async def generate(data: GenerateRequest):
    result = generate_post(data.length, data.language, data.tag)
    return {"response": result} 