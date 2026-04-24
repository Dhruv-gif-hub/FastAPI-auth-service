from fastapi import FastAPI
from .middleware.logging import RequestLoggingMiddleware
from .routes import admin , user
from .schemas import auth
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(
        title="My API",
        description="Backend for project",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # change in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(auth.router, tags=["Auth"])
    app.include_router(user.router, tags=["Users"])
    app.include_router(admin.router, tags=["Admin"])

    @app.get("/")
    def root():
        return {"message": "API is running"}

    return app


app = create_app()
