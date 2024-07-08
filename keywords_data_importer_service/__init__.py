from .importer import app


def run():
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8831)
