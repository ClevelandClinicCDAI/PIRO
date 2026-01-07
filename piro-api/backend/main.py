from apis.base import api_router
from core.config import settings
from db.base_class import Base
from db.session import SessionLocal, engine_inst
from db.utils import check_db_connected, check_db_disconnected
from exception_handlers import request_validation_exception_handler
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from logger import logger
from core.constants import Constants
from db.repository.role import ensure_role_exists
from middleware import log_request_middleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from starlette import status


def include_router(app):
    app.include_router(api_router)


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def create_tables():
    Base.metadata.create_all(bind=engine_inst)


def seed_system_roles():
    """Guarantee required system roles exist for admin drop-downs."""
    db = SessionLocal()
    try:
        ensure_role_exists(
            code=Constants.RoleSlideRoom,
            short_name="Slide Room",
            description="Slide room queue access only",
            reference="ROLE-SLIDEROOM",
            user="system",
            db=db,
        )
    except Exception as exc:  # pragma: no cover - best-effort guard
        logger.error("Unable to seed system roles: %s", exc)
    finally:
        db.close()


def start_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        debug=True,
    )
    origins = [settings.API_CORS]

    app.middleware("http")(log_request_middleware)
    app.add_exception_handler(
        RequestValidationError, request_validation_exception_handler
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    add_pagination(app)
    include_router(app)
    if settings.DATABASE == "SQLITE":
        create_tables()
    return app


app = start_application()

FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=engine_inst)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    exc_str = f"{exc}".replace("\n", "; ").replace("  ", " ")
    logger.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}

    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={
            "message": f"Oops! {exc.name} did something. "
            "There goes a rainbow..."
        },
    )


@app.on_event("startup")
async def app_startup():
    await check_db_connected()
    seed_system_roles()


@app.on_event("shutdown")
async def app_shutdown():
    await check_db_disconnected()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, port=5000)
