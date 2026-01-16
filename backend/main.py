from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os
from datetime import datetime, timedelta
from database import init_db
from models import PredictionCreate

app = FastAPI()
init_db()

# Подключаем шаблоны и статику
templates = Jinja2Templates(directory="backend/static")
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

DB_PATH = os.getenv("DATABASE_URL", "predictions.db")

@app.get("/", response_class=HTMLResponse)
async def admin_panel(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM predictions ORDER BY match_datetime DESC")
    predictions = cur.fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "predictions": predictions})

@app.post("/add")
async def add_prediction(
    league: str = Form(...),
    home_team: str = Form(...),
    away_term: str = Form(...),
    match_datetime: str = Form(...),
    prediction_type: str = Form(...),
    confidence: float = Form(...),
    reasoning: str = Form(None),
):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO predictions 
        (league, home_team, away_team, match_datetime, prediction_type, confidence, reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (league, home_team, away_term, match_datetime, prediction_type, confidence, reasoning))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.get("/api/predictions")
async def get_active_predictions():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    tomorrow = (datetime.utcnow() + timedelta(days=2)).isoformat()
    cur.execute("""
        SELECT league, home_team, away_team, match_datetime, prediction_type, confidence, reasoning
        FROM predictions
        WHERE is_active = 1 AND match_datetime BETWEEN ? AND ?
        ORDER BY match_datetime
    """, (now, tomorrow))
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "league": r[0],
            "home_team": r[1],
            "away_team": r[2],
            "match_datetime": r[3],
            "prediction_type": r[4],
            "confidence": r[5],
            "reasoning": r[6],
        }
        for r in rows
    ]