from fastapi import FastAPI
from .routers.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="Simple MCP WebApp", version="0.1.0")
    app.include_router(health_router, prefix="")
    return app


app = create_app()
