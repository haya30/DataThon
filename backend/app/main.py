from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.interview_routes import router as interview_router
from app.routes.evaluation_routes import router as evaluation_router


app = FastAPI(
    title="NUKHBA AI Interview Agent API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(interview_router)
app.include_router(evaluation_router)


@app.get("/")
async def root():
    return {
        "message": "NUKHBA AI Interview Agent API is running"
    }