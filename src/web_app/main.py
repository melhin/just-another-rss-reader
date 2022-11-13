import base64
import binascii
from typing import Optional

from pydantic import BaseModel, ValidationError, validator
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.middleware import Middleware
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.applications import Starlette
from starlette.authentication import SimpleUser, AuthCredentials, AuthenticationError, AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware

from config import settings
from db.session import make_engine, get_db_session_from_request
from db.articles import ArticleService

templates = Jinja2Templates(directory="src/web_app/templates")


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers or not settings.auth_password:
            return

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "basic":
                return
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid basic auth credentials")

        username, _, password = decoded.partition(":")
        if password == settings.auth_password:
            return AuthCredentials(["authenticated"]), SimpleUser(username)
        return None


class FeedParams(BaseModel):
    offset: Optional[int] = 0
    limit: Optional[int] = 20
    when: Optional[str] = "thisyear"

    @validator("when")
    def when_match(cls, v):
        if v not in ["today", "thisweek", "thismonth", "thisyear"]:
            raise ValueError("Invalid value for when")
        return v


async def get_articles_for_request(parsed, session):
    article_service = ArticleService(session=session)
    response = await article_service.get_articles(offset=parsed.offset, limit=parsed.limit, when=parsed.when)
    total = await article_service.get_total_articles(when=parsed.when)
    return response, total


async def get_feed(request):
    if settings.auth_password and not request.user.is_authenticated:
        return PlainTextResponse(str("User Unauthorized"), status_code=401, headers={"WWW-Authenticate": "Basic"})

    try:
        parsed = FeedParams(**request.query_params)
    except ValidationError as e:
        return JSONResponse({"error": e.json()})

    async with get_db_session_from_request(request) as session:
        response, total = await get_articles_for_request(parsed, session)
    previous = parsed.offset - parsed.limit
    next = parsed.offset + parsed.limit
    context = {
        "request": request,
        "response": response,
        "previous": previous if previous >= 0 else None,
        "next": next if next < total else None,
        "total": total,
        "when": parsed.when,
    }
    return templates.TemplateResponse("index.html", context=context)


async def ping(request):
    return PlainTextResponse("pong")


routes = [
    Route("/", get_feed),
    # Just to make sure that the app is kept alive by the free hosting providers
    Route("/ping", ping),
    Mount("/static", StaticFiles(directory="src/web_app/static"), name="static"),
]
middleware = [Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())]

app = Starlette(routes=routes, middleware=middleware)


def _setup_db(app: Starlette) -> None:  # pragma: no cover
    """
    Creates connection to the database.
    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.
    :param app: fastAPI application.
    """
    app.state.db_engine = make_engine(str(settings.db_url))


@app.on_event("startup")
async def startup():
    _setup_db(app)


@app.on_event("shutdown")
async def shutdown():
    await app.state.db_engine.dispose()
