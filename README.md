# NeuroScan AI - Brain Tumor Detection
This repository hosts a full-stack web application designed to interface with an advanced artificial intelligence model focused on medical imaging. Specifically, the machine learning pipeline is dedicated to training and deploying a model that analyzes brain scan images to identify and locate potential tumors. By providing an intuitive frontend and a robust backend API, this project aims to make the underlying tumor-detection AI accessible and easy to use for analyzing scan results.

## Team Members
- Juan Cruz
- Owen Espitia
- Erik Woodland
- Samuel Elesho

---

## Project Structure

```
├── frontend/              # Next.js web application
├── backend/               # Python FastAPI service
├── pipeline/              # ML model training & inference
├── database/              # Supabase DAL/repositories
├── infra/                 # Docker Compose configuration
└── README.md              # This file
```

---

## Quick Start

### Prerequisites
- Node.js 18+ (frontend)
- Python 3.9+ (backend, pipeline)
- Docker & Docker Compose (optional, for containerized deployment)
- Supabase project (for database)

### Environment Setup

Create `.env.local` in the `frontend/` directory:
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-publishable-key
```

Create `.env` in the `backend/` directory:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your-publishable-key
SUPABASE_SECRET_KEY=your-secret-key
```

---

## Frontend (Next.js)

The frontend is a glitch-core styled React application built with Next.js, featuring real-time MRI upload and analysis.

### Getting Started

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Features
- 🔐 Supabase authentication (Login/Signup)
- 📤 Drag-and-drop MRI image upload
- 🚀 Real-time AI analysis with confidence scores
- 💾 Secure image & prediction storage
- 🎨 Glitch-core aesthetic with neon animations

### Project Structure
```
frontend/
├── src/app/
│   ├── page.js              # Home page
│   ├── about/page.js        # About page
│   ├── contact/page.js      # Contact form
│   ├── login/page.js        # Login
│   ├── signup/page.js       # Registration
│   └── upload/page.js       # MRI upload & analysis
├── src/components/
│   ├── NavBar.js            # Navigation
│   ├── AuthProvider.js      # Auth context
│   └── ...
└── package.json
```

---

## ML Pipeline

Trains three models on the Brain Tumor MRI Dataset (Glioma / Meningioma / Pituitary / No Tumor):

| Model      | Architecture | Training | Route |
|------------|--------------|----------|-------|
| `cnn`      | SimpleCNN (4 conv blocks) | From scratch | `POST /predict` |
| `vit`      | ViT-B/16 (transfer-learned) | ImageNet weights | `POST /predict/vit` |
| `convnext` | ConvNeXt-Tiny (transfer-learned) | ImageNet weights | `POST /predict/convnext` |

### Dataset Structure
```
pipeline/data/
├── Train/
│   ├── glioma/
│   ├── meningioma/
│   ├── notumor/
│   └── pituitary/
└── Test/
    ├── glioma/
    ├── meningioma/
    ├── notumor/
    └── pituitary/
```

### Training Models

```bash
cd pipeline
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Train from scratch
python train.py --model cnn      # Options: cnn, vit, convnext
python train.py --model vit
python train.py --model convnext

# Continue training existing CNN
python finetune.py               # Only saves if validation accuracy improves

# Evaluate model
python evaluate.py               # Test set evaluation (default: cnn)
python evaluate.py --model vit
```

### Running API Locally

```bash
cd pipeline
uvicorn api:app --reload --port 8001
```

Test with:
```bash
curl -F "file=@scan.jpg" http://localhost:8001/predict
```

### Endpoints
- `GET /health` — Health check
- `GET /classes` — Available tumor classes
- `POST /predict` — CNN prediction (default)
- `POST /predict/vit` — ViT prediction
- `POST /predict/convnext` — ConvNeXt prediction

### GPU Troubleshooting

If `Using device: cpu` appears instead of `Using device: cuda`:

1. **Check GPU availability:** `nvidia-smi`
2. **Windows:** Install CUDA-enabled PyTorch:
   ```powershell
   pip uninstall torch torchvision
   pip install torch==2.13.0 torchvision==0.28.0 --extra-index-url https://download.pytorch.org/whl/cu130
   ```
3. **Verify torch build:** `pip show torch` (look for `+cu130` suffix for CUDA)
4. **Update GPU drivers** if still showing CPU

### Model Files
- `cnn_model.pt` (~1.7MB) — Committed to git
- `vit_model.pt` (~340MB) — Shared via Teams (GitHub limit)
- `convnext_model.pt` (~110MB) — Shared via Teams (GitHub limit)
- `class_names.json` — Class mapping (committed)
- Metrics & training curves (committed)

---

## Database (Supabase)

PostgreSQL database with Supabase DAL providing CRUD repositories.

### Setup

```bash
pip install -r database/requirements.txt
```

### Environment Variables
```powershell
$env:SUPABASE_URL = "https://your-project.supabase.co"
$env:SUPABASE_PUBLISHABLE_KEY = "your-publishable-key"
$env:SUPABASE_SECRET_KEY = "your-secret-key"  # Server-side only
```

### Usage

```python
from database import get_database

db = get_database()
db.check_connection()  # Verify connection

# Create records
db.users.create(user_id=1, name="Alex")
db.images.create(image_id=1, url="https://example.com/scan.png")
db.predictions.create(
    pred_id=1,
    user_id=1,
    image_id=1,
    description="Potential tumor detected",
)

# Query with joins
predictions = db.predictions.list_with_user_and_image()
# Returns: {pred_id, name, url, description, ...}
```

### Schema
- **Users** — User accounts with metadata
- **Images** — MRI scan uploads with URLs
- **Predictions** — Analysis results linked to users & images

---

## Backend (FastAPI)

Python FastAPI service that coordinates the ML pipeline, Supabase database, and authentication.

### Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Runs on `http://localhost:8000`

### Endpoints
- `POST /predict` — Analyze MRI image and store prediction
- `GET /predictions` — Retrieve user's predictions
- `POST /auth/login` — Supabase authentication
- `POST /auth/logout` — Sign out

---

## Docker Deployment

Deploy all services with Docker Compose:

```bash
cd infra
docker-compose up --build
```

Services:
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **Pipeline API:** http://localhost:8001

### Environment Setup
Copy `.env.example` to `.env` and fill in your Supabase credentials:
```bash
cp .env.example .env
```

---

## Git Workflow

### Branch & PR Convention
- **No Direct Pushes to Main**: After initial setup, `main` is protected.
- **Branching**: Create feature/bugfix branches off `main`.
- **Pull Requests**: Open PR when ready to merge.
- **Review & Approval**: Requires ≥1 approval before merge.
- **Committing Identity**: **Always commit with your own Git identity** (name + email). This is required for weekly contribution grading.

### Example Workflow
```bash
git checkout -b feature/my-feature
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
# Open PR on GitHub
```

---

## Development Tips

### Running All Services Locally

Terminal 1: Frontend
```bash
cd frontend && npm run dev
```

Terminal 2: Backend
```bash
cd backend && python main.py
```

Terminal 3: Pipeline API
```bash
cd pipeline && uvicorn api:app --reload --port 8001
```

### Troubleshooting
- **Port already in use:** Change port in run commands or kill existing process
- **Supabase connection failing:** Verify `.env` credentials and network access
- **Model files missing:** Grab `vit_model.pt` and `convnext_model.pt` from Teams
- **Build errors:** Ensure Python 3.9+, Node.js 18+

---

## Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Supabase Docs](https://supabase.com/docs)
- [PyTorch Docs](https://pytorch.org/docs/)
- [Docker Docs](https://docs.docker.com/)

---

## License

This project is part of Q4 AI Projects coursework.

---

## Support

For issues or questions, open a GitHub issue or contact the team members above.
