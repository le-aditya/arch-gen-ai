import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).parent.parent / ".env")

from app.database.db import init_db  # noqa: E402
from app.routes import analyze, generation, prediction, reports, requirements  # noqa: E402

init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="ARCH GEN AI", version="2.0", lifespan=lifespan)

_default_origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174"]
_extra_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins + _extra_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(requirements.router)
app.include_router(prediction.router)
app.include_router(generation.router)
app.include_router(analyze.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "ok"}
