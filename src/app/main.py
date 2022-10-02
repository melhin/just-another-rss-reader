from typing import Optional

from pydantic import BaseModel, ValidationError, validator
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.applications import Starlette

from src.db.articles import ArticleService
from src.db.session import make_engine, make_session_factory, get_db_session_from_request

templates = Jinja2Templates(directory="src/app/templates")


class FeedParams(BaseModel):
    offset: Optional[int] = 0
    limit: Optional[int] = 10
    when: Optional[str] = "thisyear"

    @validator("when")
    def when_match(cls, v):
        if v not in ["today", "thisweek", "thismonth"]:
            raise ValueError("Invalid value for when")
        return v


async def get_feed(request):
    try:
        parsed = FeedParams(**request.query_params)
    except ValidationError as e:
        return JSONResponse({"error": e.json()})

    async with get_db_session_from_request(request) as session:
        article_service = ArticleService(session=session)
        response = await article_service.get_articles(offset=parsed.offset, limit=parsed.limit, when=parsed.when)
        total = await article_service.get_total_articles(when=parsed.when)
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


routes = [
    Route("/", get_feed),
    Mount("/static", StaticFiles(directory="src/app/static"), name="static"),
]

app = Starlette(debug=True, routes=routes)


def _setup_db(app: Starlette) -> None:  # pragma: no cover
    """
    Creates connection to the database.
    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.
    :param app: fastAPI application.
    """
    app.state.db_engine = make_engine()
    app.state.db_session_factory = make_session_factory(app.state.db_engine)


@app.on_event("startup")
async def startup():
    _setup_db(app)


@app.on_event("shutdown")
async def shutdown():
    await app.state.db_engine.dispose()
