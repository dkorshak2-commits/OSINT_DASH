import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import dns.resolver
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("OSINT_DB", BASE_DIR / "osint_dash.db"))
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="OSINT Dash", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class TargetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    target_type: str = Field(default="website", pattern="^(name|website|business)$")
    notes: str = Field(default="", max_length=2000)


def db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_type TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(target_id) REFERENCES targets(id) ON DELETE CASCADE
        )"""
    )
    connection.commit()
    return connection


def clean_domain(value: str) -> str:
    parsed = urlparse(value if "://" in value else f"https://{value}")
    return parsed.hostname or value.strip()


def run_passive_scan(target_id: int, target: str):
    domain = clean_domain(target)
    results = []
    try:
        for record_type in ("A", "AAAA", "MX", "NS", "TXT"):
            try:
                answers = dns.resolver.resolve(domain, record_type, lifetime=5)
                values = [str(answer) for answer in answers]
                results.append({"record_type": record_type, "values": values})
            except Exception:
                continue
    except Exception as exc:
        results.append({"error": str(exc)})

    try:
        url = target if "://" in target else f"https://{target}"
        response = requests.get(url, timeout=8, allow_redirects=True, headers={"User-Agent": "OSINT-Dash/1.0"})
        results.append({
            "website": {
                "final_url": response.url,
                "status_code": response.status_code,
                "server": response.headers.get("server", ""),
                "content_type": response.headers.get("content-type", ""),
                "security_headers": {
                    header: response.headers.get(header, "")
                    for header in ("content-security-policy", "strict-transport-security", "x-frame-options", "x-content-type-options")
                },
            }
        })
    except requests.RequestException as exc:
        results.append({"website_error": str(exc)})

    connection = db()
    connection.execute(
        "INSERT INTO findings(target_id, source, data, created_at) VALUES (?, ?, ?, ?)",
        (target_id, "passive_recon", json.dumps(results), datetime.now(timezone.utc).isoformat()),
    )
    connection.commit()
    connection.close()
    return results


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/targets")
def list_targets():
    connection = db()
    rows = connection.execute("SELECT * FROM targets ORDER BY id DESC").fetchall()
    connection.close()
    return [dict(row) for row in rows]


@app.post("/api/targets", status_code=201)
def create_target(payload: TargetCreate):
    connection = db()
    cursor = connection.execute(
        "INSERT INTO targets(name, target_type, notes, created_at) VALUES (?, ?, ?, ?)",
        (payload.name.strip(), payload.target_type, payload.notes.strip(), datetime.now(timezone.utc).isoformat()),
    )
    connection.commit()
    target_id = cursor.lastrowid
    connection.close()
    return {"id": target_id, **payload.model_dump()}


@app.delete("/api/targets/{target_id}", status_code=204)
def delete_target(target_id: int):
    connection = db()
    connection.execute("DELETE FROM findings WHERE target_id = ?", (target_id,))
    cursor = connection.execute("DELETE FROM targets WHERE id = ?", (target_id,))
    connection.commit()
    connection.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Target not found")


@app.post("/api/targets/{target_id}/scan")
def scan_target(target_id: int):
    connection = db()
    target = connection.execute("SELECT * FROM targets WHERE id = ?", (target_id,)).fetchone()
    connection.close()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return {"target": dict(target), "findings": run_passive_scan(target_id, target["name"])}


@app.get("/api/targets/{target_id}/findings")
def target_findings(target_id: int):
    connection = db()
    rows = connection.execute("SELECT * FROM findings WHERE target_id = ? ORDER BY id DESC", (target_id,)).fetchall()
    connection.close()
    return [{**dict(row), "data": json.loads(row["data"])} for row in rows]
