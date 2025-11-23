from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from .routers.health import router as health_router
from .routers.mcp import router as mcp_router

# Load .env file from app directory
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


def create_app() -> FastAPI:
    app = FastAPI(title="Simple MCP WebApp", version="0.1.0")
    app.include_router(health_router, prefix="")
    app.include_router(mcp_router)
    return app


app = create_app()
