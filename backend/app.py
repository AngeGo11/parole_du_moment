"""Application FastAPI principale."""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Home import router as home_router
from Profile import router as profile_router
from Assistant import router as assistant_router

load_dotenv()


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Parole du Moment API",
    version="1.0.0",
    description="API Spirituelle - Home (LangChain + MongoDB)",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "home"}


app.include_router(home_router)
app.include_router(profile_router)
app.include_router(assistant_router)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {"message": "Bienvenue sur Parole du Moment API"}

