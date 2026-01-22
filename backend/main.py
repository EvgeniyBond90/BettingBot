from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os
from datetime import datetime, timedelta

app = FastAPI()

templates = Jinja2Templates(directory="backend/static")
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

DB_PATH = os.getenv("DATABASE_URL", "predictions.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league TEXT NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            match_datetime TEXT NOT NULL,
            prediction_type TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", response_class=HTMLResponse)
async def admin_panel(request: Request):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM predictions ORDER BY match_datetime DESC")
    predictions = cur.fetchall()
    db.close()
    predictions = [dict(row) for row in predictions]
    return templates.TemplateResponse("index.html", {"request": request, "predictions": predictions})

@app.post("/add")
async def add_prediction(
    league: str = Form(...),
    home_team: str = Form(...),
    away_team: str = Form(...),
    match_datetime: str = Form(...),
    prediction_type: str = Form(...),
):
    db = get_db()
    cur = db.cursor()
    dt_iso = f"{match_datetime}:00"
    cur.execute("""
        INSERT INTO predictions
        (league, home_team, away_team, match_datetime, prediction_type)
        VALUES (?, ?, ?, ?, ?)
    """, (league, home_team, away_team, dt_iso, prediction_type))
    db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{prediction_id}")
async def delete_prediction(prediction_id: int):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
    db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=303)

@app.get("/api/predictions")
async def get_active_predictions():
    db = get_db()
    cur = db.cursor()
    now = datetime.utcnow().isoformat()
    future = (datetime.utcnow() + timedelta(days=2)).isoformat()
    cur.execute("""
        SELECT league, home_team, away_team, match_datetime, prediction_type
        FROM predictions
        WHERE is_active = 1 AND match_datetime BETWEEN ? AND ?
        ORDER BY match_datetime
    """, (now, future))
    rows = cur.fetchall()
    db.close()
    result = [
        {
            "league": r["league"],
            "home_team": r["home_team"],
            "away_team": r["away_team"],
            "match_datetime": r["match_datetime"],
            "prediction_type": r["prediction_type"],
        }
        for r in rows
    ]
    return result
