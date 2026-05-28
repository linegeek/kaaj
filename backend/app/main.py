from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import router as api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all rule evaluators are registered on startup
    from app.engine.rules.registry import RuleEvaluatorRegistry
    RuleEvaluatorRegistry.ensure_loaded()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Kaaj",
        description="Equipment finance loan underwriting and lender matching platform",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()
