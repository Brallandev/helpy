from fastapi import FastAPI
from src.api import config, questions, answers
import uvicorn

app = FastAPI(title="Multi-Agent Diagnostic API")

# Include routers
app.include_router(config.router, prefix="/config", tags=["config"])
app.include_router(questions.router, prefix="/questions", tags=["questions"])
app.include_router(answers.router, prefix="/answers", tags=["answers"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Multi-Agent API is running"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)