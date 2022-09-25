from typing import Optional

from pydantic import BaseModel, ValidationError, validator
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.applications import Starlette

from src.db import connection
from src.db.articles import Article

templates = Jinja2Templates(directory="src/app/templates")


class FeedParams(BaseModel):
    offset: Optional[int] = 0
    limit: Optional[int] = 25
    when: Optional[str] = "today"

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

    async with connection() as db_conn:
        article = Article()
        response = await article.get_articles(
            connection=db_conn, offset=parsed.offset, limit=parsed.limit, when=parsed.when
        )
        total = await article.get_total_articles(db_conn, when=parsed.when)
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


def startup():
    pass


routes = [
    Route("/", get_feed),
    Mount("/static", StaticFiles(directory="src/app/static"), name="static"),
]

app = Starlette(debug=True, routes=routes, on_startup=[startup])
