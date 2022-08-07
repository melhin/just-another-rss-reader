import sys
import uvicorn
from src.app.main import app


if __name__ == "__main__":
    try:
        port = sys.argv[1]
    except IndexError:
        port = 5000
    uvicorn.run('app.main:app', host='0.0.0.0', port=port, reload=True)
