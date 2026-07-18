# Resume Updater & ATS Optimizer

A production-quality AI-powered application to tailor your resume for every job application while preserving the original. Built with **Next.js 14**, **FastAPI**, and **OpenAI**.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Resume Upload** | Upload DOCX or PDF resumes with intelligent parsing |
| 📊 **ATS Scoring** | Comprehensive 0–100 ATS score with breakdown by keyword, formatting, experience, and readability |
| 🔍 **JD Analysis** | Paste text or a URL to automatically scrape and parse any job posting |
| 🎯 **Gap Analysis** | Identify missing skills, weak bullets, and ATS score improvement potential |
| ✨ **AI Optimization** | GPT-4o powered resume optimization — never fabricates, only rewrites existing content |
| 📝 **Change Report** | Markdown diff report showing exactly what changed and why |
| 👁️ **Resume Diff** | Side-by-side highlighted diff view (like GitHub) |
| 💾 **Versioning** | Original always preserved; each optimization creates a new named version |
| 📤 **Export** | Download as DOCX, PDF, Markdown report, or JSON |

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (recommended)
- Or: **Python 3.11+** and **Node.js 20+** for local development
- An **OpenAI API key** (GPT-4o access required)

---

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd "resume-updater"

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env and add your OPENAI_API_KEY

# 3. Start everything
docker compose up --build

# 4. Open the app
open http://localhost:3000
```

---

### Option 2: Local Development

#### Backend

```bash
cd resume-updater/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

#### Frontend

```bash
cd resume-updater/frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The app will be available at `http://localhost:3000`

---

## 🔧 Environment Variables

### Backend (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ | — | Your OpenAI API key (GPT-4o access needed) |
| `DATABASE_URL` | ❌ | `sqlite+aiosqlite:///./resume_updater.db` | Database URL (SQLite or PostgreSQL) |
| `UPLOAD_DIR` | ❌ | `./uploads` | Directory for uploaded resume files |
| `EXPORT_DIR` | ❌ | `./exports` | Directory for exported DOCX/PDF files |
| `LIBREOFFICE_PATH` | ❌ | `/usr/bin/libreoffice` | Path to LibreOffice binary |
| `MAX_FILE_SIZE_MB` | ❌ | `10` | Maximum upload file size in MB |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

### Frontend (`.env.local`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | ❌ | `http://localhost:8000/api/v1` | Backend API URL |

---

## 🗄️ Switching to PostgreSQL

Change `DATABASE_URL` in your `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/resume_updater
```

Install the async driver:
```bash
pip install asyncpg
```

Run migrations:
```bash
alembic upgrade head
```

No other code changes needed.

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload` | Upload DOCX or PDF resume |
| `POST` | `/api/v1/ats-score` | Calculate ATS score |
| `POST` | `/api/v1/job-description` | Submit job description (text or URL) |
| `POST` | `/api/v1/analyze-gap` | Analyze resume vs JD gap |
| `POST` | `/api/v1/optimize` | Generate optimized resume version |
| `GET` | `/api/v1/resume/{id}` | Get resume by ID |
| `GET` | `/api/v1/download/docx/{id}` | Download DOCX |
| `GET` | `/api/v1/download/pdf/{id}` | Download PDF |
| `GET` | `/api/v1/changes/{id}` | Get change report |
| `GET` | `/api/v1/health` | Health check |

Full interactive docs: `http://localhost:8000/docs`

---

## 🧪 Running Tests

```bash
cd resume-updater/backend
source venv/bin/activate
pytest tests/ -v --cov=. --cov-report=html
open htmlcov/index.html
```

---

## 📁 Project Structure

```
resume-updater/
├── backend/
│   ├── main.py                # FastAPI app entry point
│   ├── config.py              # Settings (pydantic-settings)
│   ├── database.py            # Async SQLAlchemy setup
│   ├── models/                # ORM models
│   ├── schemas/               # Pydantic request/response schemas
│   ├── api/routes/            # Route handlers
│   ├── resume_parser/         # DOCX + PDF parsing
│   ├── ats/                   # ATS scoring engine
│   ├── jd_parser/             # Job description parser + URL scraper
│   ├── optimizer/             # AI-powered resume optimizer
│   ├── export/                # DOCX + PDF generation
│   ├── prompts/               # LLM prompt templates
│   └── tests/                 # pytest test suite
├── frontend/
│   ├── app/                   # Next.js App Router pages
│   ├── components/            # UI components
│   ├── lib/                   # API client, store, utilities
│   ├── types/                 # TypeScript type definitions
│   └── hooks/                 # Custom React hooks
└── docker-compose.yml
```

---

## 🤖 AI Safety & Anti-Hallucination

The optimizer is explicitly instructed to **never fabricate**:
- ❌ Companies or employers you didn't work at
- ❌ Projects you didn't build
- ❌ Metrics or numbers not in your resume
- ❌ Skills or technologies you don't have

If a JD requires a skill not present in your resume, the AI will report:  
`"Cannot add — no supporting evidence in original resume."`

---

## 📝 License

MIT License — see [LICENSE](./LICENSE) for details.
