import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import router as auth_router
from journal.router import router as journal_router

app = FastAPI(
    title="Log Journal API",
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
    return {"message": "API is healthy"}


app.include_router(auth_router, prefix="")
app.include_router(journal_router, prefix="")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)