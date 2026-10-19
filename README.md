<div align="center">
  <h1>CAT-Guard</h1>
  <p><strong>Catchment-area forest monitoring and threat intelligence.</strong></p>
  <p>Connect geospatial analysis, field observations, sensor telemetry, and auditable alerts in one conservation-focused platform.</p>
  <p>
    <img src="https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-3178C6?logo=typescript&logoColor=white" alt="React and TypeScript">
    <img src="https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/Database-PostgreSQL%20%2B%20PostGIS-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL and PostGIS">
    <img src="https://img.shields.io/badge/License-MIT-2ea44f" alt="MIT License">
  </p>
</div>

CAT-Guard is a full-stack forest-monitoring platform concept for Catchment Area Treatment (CAT) zones. It brings together satellite imagery analysis, sensor telemetry, threat-detection workflows, geospatial dashboards, and community field reports.

> **Project status:** This repository describes an engineering platform and its intended workflows. Satellite-derived indicators, ML detection, sensor readings, maps, and alerts should be validated against real data and field conditions before being used for environmental or operational decisions.

---

## Features

| Module | Description |
|---|---|
| 🛰️ Satellite Imagery | NDVI/SAVI computation, change detection, imagery ingestion |
| 🤖 ML Detection | CNN-based illegal logging & anomaly detection (YOLOv8-ready) |
| 📡 IoT Sensors | Multi-protocol sensor network with real-time time-series data |
| 🔔 Alert Engine | Rule-based alerting with WebSocket streaming & multi-channel delivery |
| 📊 Analytics | Interactive dashboards with Recharts + MapLibre GL maps |
| 👥 Community | Field reporting portal with GPS tagging & verification workflow |
| 🔐 RBAC Auth | 5-tier role-based access control with JWT + refresh tokens |
| 📄 Reports | PDF, CSV, GeoJSON report generation |
| 🔗 Audit Trail | SHA-256 cryptographic audit log for data integrity |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| State Management | Zustand |
| Maps | MapLibre GL JS + react-map-gl |
| Charts | Recharts + D3.js |
| Backend | Python 3.11, FastAPI |
| Database | PostgreSQL 16 + PostGIS 3 + TimescaleDB |
| Cache / Queue | Redis 7 |
| Object Storage | MinIO (dev) / AWS S3 (prod) |
| Real-time | FastAPI WebSocket + Redis Pub/Sub |
| ORM | SQLAlchemy 2.0 async + GeoAlchemy2 |
| Migrations | Alembic |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) >= 24.0
- [Node.js](https://nodejs.org/) >= 20.0
- [pnpm](https://pnpm.io/) >= 9.0 (`npm install -g pnpm`)
- [Python](https://www.python.org/) >= 3.11 (for local development)

---

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/kishorekrrish3/catguard.git
cd catguard
cp .env.example .env
# Edit .env and set SECRET_KEY to a random 32+ char string
```

### 2. Start the full stack

```bash
docker compose up -d
```

Services:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001
- **pgAdmin** (dev): http://localhost:5050

### 3. Run database migrations and seed data

```bash
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed.py
```

### 4. Configure access

Use the account and password configuration defined by your local environment and seed setup. Do not publish shared demo credentials or deploy with predictable passwords. For any deployment, provision unique credentials, set a strong secret key, and disable or change any development-only accounts before exposing the service.


---

## Development Setup (without Docker)

### Backend

```bash
cd apps/api
python -m venv .venv
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Unix
pip install -r requirements.txt
cp ../../.env.example .env
# Start DB + Redis with docker compose up -d db redis minio
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

### Frontend

```bash
cd apps/web
pnpm install
pnpm dev
```

---

## Project Structure

```
catguard/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py         # App factory
│   │   │   ├── config.py       # Settings
│   │   │   ├── models/         # SQLAlchemy ORM models
│   │   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── routers/        # API route handlers
│   │   │   ├── services/       # Business logic
│   │   │   ├── core/           # Auth, Redis, WebSocket, Storage
│   │   │   └── ml/             # Detection engine, NDVI
│   │   ├── alembic/            # Database migrations
│   │   ├── tests/
│   │   └── requirements.txt
│   └── web/                    # React frontend
│       └── src/
│           ├── api/            # Axios API client
│           ├── components/     # Reusable UI components
│           ├── hooks/          # Custom React hooks
│           ├── pages/          # Route-level pages
│           ├── store/          # Zustand state stores
│           └── types/          # TypeScript types
├── infra/
│   ├── nginx/                  # Reverse proxy
│   └── db/                     # DB init SQL
├── scripts/                    # Utility scripts
├── docs/                       # Architecture docs
├── .github/workflows/          # CI/CD
├── docker-compose.yml
└── README.md
```

---

## API Documentation

FastAPI auto-generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Running Tests

```bash
# Backend
cd apps/api
pytest tests/ -v --cov=app

# Frontend
cd apps/web
pnpm test
```

---

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please ensure all tests pass and code is linted before submitting.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built for forest conservation. 🌿*
