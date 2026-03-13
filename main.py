from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import Base, engine
from routers import users, tasks

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description="Scalable REST API with JWT authentication and role-based access control.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(users.router, prefix="/api/v1", tags=["Auth & Users"])
app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])

# Serve frontend if the folder exists
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
