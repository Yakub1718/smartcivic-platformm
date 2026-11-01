# SmartCivic — AI-assisted Municipal Issue Reporting

A runnable full-stack academic MVP. React/Vite frontend, FastAPI backend, SQLAlchemy database (SQLite by default; PostgreSQL through `DATABASE_URL`), JWT authentication, role-based workflows, image uploads, geolocation fields, and an explainable AI triage service.

## Important implementation boundary
The included triage service is a **baseline rule-based prototype**, not a trained YOLO model. It uses the citizen's description and selected category to suggest department/severity/priority. The AI service is deliberately isolated so a trained YOLO/OpenCV inference pipeline can replace it later. Do not claim real object detection until trained weights and evaluation data are integrated.

## Requirements
- Node.js 20+ and npm
- Python 3.11+
- (Optional) PostgreSQL

## Run backend
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
API docs: http://127.0.0.1:8000/docs

SQLite is used automatically. To use PostgreSQL, set `DATABASE_URL` in `backend/.env`, for example:
`postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/smartcivic`

## Run frontend
Open a second terminal:
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Open http://localhost:5173

## Demo flow
1. Register a citizen account in the app.
2. Log in and submit an issue with description, category, optional image and location.
3. Open My Complaints to track status.
4. Register another account and choose `OFFICER` only for a local academic demo. In a real deployment, officer/admin roles must be assigned by an administrator, not self-selected.
5. Officer can update status and add resolution notes.

## Roles
- `CITIZEN`: create and view own complaints.
- `OFFICER`: view all complaints and update their status.
- `ADMIN`: same MVP access as officer; production permissions should be narrowed and audited.

## GitHub
Commit the project files, but never commit `.env`, database files, uploaded citizen images, secrets, or trained model weights. `.gitignore` excludes these.
