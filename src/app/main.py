from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from src.db import connection
from src.db.articles import Article


templates = Jinja2Templates(directory='src/app/templates')

async def homepage(request):
    async with connection() as db_conn:
        response = await Article().get_articles(connection=db_conn, offset=200)
        print(response)
    return templates.TemplateResponse('index.html', {'request': request, 'response': response})

def startup():
    print('Ready to go')


routes = [
    Route('/', homepage),
    Mount('/static', StaticFiles(directory="src/app/static"), name='static'),
]

app = Starlette(debug=True, routes=routes, on_startup=[startup])
