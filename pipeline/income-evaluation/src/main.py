from fastapi import FastAPI
from income_evaluation.router import router as income_router

app = FastAPI(title="Income Evaluation API")
app.include_router(income_router)