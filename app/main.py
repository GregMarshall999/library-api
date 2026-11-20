from fastapi import FastAPI

from app.api import books, loans, members
from app.api.errors import register_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Library API")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(books.router)
    app.include_router(members.router)
    app.include_router(loans.router)
    register_error_handlers(app)

    return app


app = create_app()
