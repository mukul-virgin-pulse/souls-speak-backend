from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import router as app_router
 
app = FastAPI()
 
# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
 
app.include_router(app_router)
 
 
@app.get("/")
async def root():
    return {"message": "Hello World"}
 
 