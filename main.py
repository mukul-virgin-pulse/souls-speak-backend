from fastapi import FastAPI
from router import router as app_router
app = FastAPI()


app.include_router(app_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}