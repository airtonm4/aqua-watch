from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.database import DatabaseSession
from app.server.routes import auth


app = FastAPI(
    title="Aqua-Watch - Local Server",
    description="""
        This server is supposed to handle the communication between the WEB (FrontEnd) and all the sensors in the pound.
    """,
    version="1.0.0",
)

origins = ["http://localhost", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(auth.router)


@app.middleware("http")
async def open_session(request: Request, call_next):
    with DatabaseSession():
        response: StreamingResponse = await call_next(request)

    return response


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "aqua-watch-local"}


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Aqua-Watch API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {"auth": "/auth", "examples": "/example", "health": "/health"},
    }
