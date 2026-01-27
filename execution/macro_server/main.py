from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Change to absolute imports for uvicorn
import models
from database import engine
from routers import indicators, values
# Note: dashboard removed - it requires core.database which is in the main agent container

# Create tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Forex Agent Macro Server")

# Global Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"data": None, "error": str(exc), "meta": None},
    )

# Include Routers
app.include_router(indicators.router)
app.include_router(values.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "macro-data-server"}
