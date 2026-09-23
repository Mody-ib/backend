from fastapi import FastAPI
from recipe import router

app = FastAPI(
    title="Recipe API Service"
)

app.include_router(router)
