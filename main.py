from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from auth.router import router as auth_router

app = FastAPI(
    title="Anime Lounge API",
    docs_url="/docs",
    openapi_url="/openapi.json",
    version="0.0.1",
)

# Allow local dev servers (Vite default or custom 8080)
origins = [
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"message": "Anime Lounge API in FastAPI"}


app.include_router(auth_router, prefix="")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)