
from fastapi import FastAPI

from app.routers.products import router as products_router
from app.routers.auth import router as auth_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Product API",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "Product API is running"}
