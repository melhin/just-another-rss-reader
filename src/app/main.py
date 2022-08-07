from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates


templates = Jinja2Templates(directory='src/app/templates')

async def homepage(request):
    return templates.TemplateResponse('index.html', {'request': request})

def startup():
    print('Ready to go')


routes = [
    Route('/', homepage),
    Mount('/static', StaticFiles(directory="src/app/static"), name='static'),
]

app = Starlette(debug=True, routes=routes, on_startup=[startup])
