from fastapi import FastAPI
from .middleware.logging import RequestLoggingMiddleware
from .routes import admin , user
from .schemas import auth
from fastapi.middleware.cors import CORSMiddleware

# This is the main entry point of the application. 
# It creates the FastAPI app, adds middleware, and includes the routers for different endpoints.
def create_app() -> FastAPI:
    app = FastAPI(
        title="My API",
        description="Backend for project",
        version="1.0.0"
    )
# CORS middleware is added to allow cross-origin requests. 
# In production, you should specify the allowed origins instead of using "*".
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Custom middleware for logging requests is added to the app.
    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(auth.router, tags=["Auth"])
    app.include_router(user.router, tags=["Users"])
    app.include_router(admin.router, tags=["Admin"])

    @app.get("/")
    def root():
        return {"message": "API is running"}

    return app


app = create_app()