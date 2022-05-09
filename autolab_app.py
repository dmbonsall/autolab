from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from restful_runner.api import app as restful_runner_api


app = FastAPI()
app.mount("/api/v1", restful_runner_api)
app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")
