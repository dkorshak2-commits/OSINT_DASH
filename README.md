# OSINT Dash

A browser-based FastAPI workspace for organizing targets and running lightweight passive reconnaissance checks.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. API documentation remains available at `/docs`.

The web UI supports creating, selecting, scanning, and deleting targets. Scans collect DNS records and basic HTTP response/security-header context. Use only against systems you own or are explicitly authorized to assess; the app is not an authorization bypass or a replacement for a bug-bounty program's scope rules.
