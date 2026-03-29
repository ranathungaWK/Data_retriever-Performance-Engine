from fastapi import FastAPI
from app.api.v1.routes import dropdown, metrics

app = FastAPI(
    title="metrics retriever" ,
    description="collecting metrics according to give test rounds or time ranges",
    version="1.0.0"
)

app.include_router(
    metrics.router,
    prefix="/api/v1/metrics",
    tags=["metrics retrieving"]
)

app.include_router(
    dropdown.router,
    prefix="/api/v1/applications",
    tags=["applications & test rounds"]
)

@app.get("/")
async def root():
    return {"message": "Data Retriever API is Online", "status": "healthy"}
