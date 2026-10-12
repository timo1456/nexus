# Nexus — Network Intelligence Workspace

Nexus is a Flask-powered network and infrastructure management platform for interactive topology mapping, device inventory, simulated monitoring, incident tracking, and rule-based troubleshooting. It brings network context and operational clues into one engineer-friendly workspace.

> **Monitoring is simulated in this release.** The application does not probe, configure, or claim to monitor physical devices. Real-device checks must be added deliberately and used only on systems you are authorised to assess.

## Features

- Modular Flask application factory, SQLAlchemy models, password hashing, session authentication, and CSRF-protected forms.
- Private account-scoped networks, device inventory, and incident access.
- Responsive dark operations dashboard with device inventory, monitoring activity, incident summaries, and network map preview.
- Interactive Cytoscape.js topology canvas with device status styling.
- Six-device demo workspace with historical observations and an example incident.
- Simulated monitoring checks, incident resolution, and deterministic troubleshooting guidance.
- SQLite local development and PostgreSQL support, Gunicorn deployment entry point, and test suite foundations.

## Run locally

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Set a strong secret key before starting. For PowerShell:

```powershell
$env:SECRET_KEY = "replace-with-a-long-random-secret"
```

Then run:

```bash
python run.py
```

Open http://127.0.0.1:5000, create an account, and click **Load demo workspace**.

Run automated tests with `python -m pytest`.

## Deployment

Configure these environment variables with your hosting provider:

- `SECRET_KEY`: a long, randomly generated secret.
- `DATABASE_URL`: managed PostgreSQL connection URL for persistent production data.
- `COOKIE_SECURE=1`: enable secure session cookies when served over HTTPS.

Start command: `gunicorn run:app`. For Render, use build command `pip install -r requirements.txt` and start command `gunicorn run:app`. The repository includes a Procfile. Attach managed PostgreSQL for production; the local SQLite database is intended for development.

## Project description

**Nexus is a Flask-based network observability and infrastructure management workspace for interactive topology mapping, device inventory, simulated monitoring, incident tracking, and rule-based troubleshooting.**

## Honest scope and roadmap

The current release uses simulated monitoring and deterministic diagnostic rules. The diagnosis engine is decision support, not a verified root-cause detector or AI model. Persistent topology edges/layout, scheduled background monitoring, authorised real ICMP/SNMP probes, notifications, database migrations, team roles, audit events, and AI integrations remain future enhancements rather than advertised finished features.
