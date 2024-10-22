import json
import uuid
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import numpy as np

from database.models import Base, Page, ContentChunk

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./database/web_crawler.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

app = FastAPI()

# Pydantic models
class RecallRequest(BaseModel):
    query: str

class RecallResponse(BaseModel):
    results: List[dict]

class StorageRequest(BaseModel):
    page_id: str
    content: str

class StorageResponse(BaseModel):
    success: bool

# Utility functions
def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    a = np.array(vec1)
    b = np.array(vec2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@app.post("/recall", response_model=RecallResponse)
async def recall(request: RecallRequest):
    # Embed the query
    import openai
    OPENAI_API_KEY = "your-openai-api-key"  # Replace with your OpenAI API key
    openai.api_key = OPENAI_API_KEY

    try:
        response = openai.Embedding.create(
            input=request.query,
            model="text-embedding-ada-002"
        )
        query_embedding = response['data'][0]['embedding']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {e}")

    # Fetch all embeddings from the database
    async with async_session() as session:
        result = await session.execute(select(ContentChunk))
        chunks = result.scalars().all()

    # Compute similarities
    similarities = []
    for chunk in chunks:
        embedding = json.loads(chunk.embedding)
        similarity = cosine_similarity(query_embedding, embedding)
        similarities.append((similarity, chunk.content))

    # Sort by similarity
    similarities.sort(reverse=True, key=lambda x: x[0])

    # Return top 5 results
    top_results = [{"score": sim, "content": cont} for sim, cont in similarities[:5]]

    return RecallResponse(results=top_results)

@app.post("/storage", response_model=StorageResponse)
async def store(request: StorageRequest):
    async with async_session() as session:
        # Fetch the page
        result = await session.execute(select(Page).where(Page.id == request.page_id))
        page = result.scalar_one_or_none()
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")

        # Create a new content chunk
        embedding = []  # Compute embedding as needed
        new_chunk = ContentChunk(
            id=str(uuid.uuid4()),
            page_id=page.id,
            content=request.content,
            embedding=json.dumps(embedding)  # Replace with actual embedding
        )
        session.add(new_chunk)
        await session.commit()

    return StorageResponse(success=True)
