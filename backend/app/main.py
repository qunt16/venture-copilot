"""
venture-copilot — FastAPI application entrypoint.
Iteration 5: Export generator added.
"""
import mimetypes

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import business_plan, document, export, finance, frameworks, health, projects, research, review, sections

app = FastAPI(
    title="Venture Copilot API",
    description="Finance-first AI business planning platform for university startup teams.",
    version="0.3.0",
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


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "data": None, "message": "Internal server error"},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "data": None, "message": exc.detail},
    )


app.include_router(health.router)
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(finance.router, prefix="/projects", tags=["finance"])
app.include_router(business_plan.router, prefix="/projects", tags=["business-plan"])
app.include_router(research.router, prefix="/projects", tags=["research"])
app.include_router(export.router, prefix="/projects", tags=["export"])
app.include_router(frameworks.router, prefix="/projects", tags=["frameworks"])
app.include_router(review.router, prefix="/projects", tags=["review"])
app.include_router(sections.router, prefix="/projects", tags=["sections"])
app.include_router(document.router, prefix="/projects", tags=["document"])
mimetypes.add_type("application/pdf", ".pdf")
mimetypes.add_type("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx")
app.mount("/exports", StaticFiles(directory="exports"), name="exports")
