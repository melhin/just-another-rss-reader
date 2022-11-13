import uvicorn
import os


if __name__ == "__main__":
    port = int(os.getenv("RUN_PORT", 5000))
    reload = os.getenv("RUN_RELOAD", False)
    workers = int(os.getenv("RUN_WORKERS", 0))or None
    uvicorn.run("web_app.main:app", host="0.0.0.0", port=port, reload=reload, workers=workers)
