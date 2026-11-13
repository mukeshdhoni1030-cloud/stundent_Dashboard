# Student Dashboard – School Management System

A web-based School Management System with separate dashboards for Principals, Teachers, and Students.

The application helps schools manage student information, attendance, marks, examinations, fees, teachers, and other academic activities.

## 1. Project Overview

The Student Dashboard is designed to simplify school administration through a centralized web application.

### User Roles

- **Principal:** Manage students, teachers, classes, subjects, and school activities.
- **Teacher:** Access assigned classes, manage attendance, and handle academic activities.
- **Student:** View personal academic information, attendance, marks, and other available details.

## 2. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React.js |
| Frontend Tool | Vite |
| Styling | CSS |
| API Communication | Axios |
| Backend | Python FastAPI |
| Database | PostgreSQL |
| Cloud Database | Neon |
| Authentication | JWT |
| ORM | SQLAlchemy |
| Backend Hosting | Vercel |
| Frontend Hosting | Vercel |
| Version Control | Git and GitHub |

## 3. Project Structure

```text
student-dashboard/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── limiter.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── student.py
│   │   │   ├── teacher.py
│   │   │   └── principal.py
│   │   └── seed_data.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── index.html
│
├── .gitignore
└── README.md
```

## 4. Prerequisites

Install the following software:

- Python 3.10 or compatible version
- Node.js and npm
- PostgreSQL (for local database development)
- Visual Studio Code
- Git

## 5. Backend Setup

Open the terminal and navigate to the backend folder:

```bash
cd backend
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the virtual environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file inside the backend folder.

Example:

```env
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Never upload actual passwords, database URLs, or secret keys to GitHub.

### Run the backend

```bash
uvicorn app.main:app --reload
```

Backend local URL:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## 6. Frontend Setup

Open another terminal and navigate to the frontend folder:

```bash
cd frontend
```

### Install dependencies

```bash
npm install
```

### Configure the API URL

Create a `.env` file inside the frontend folder:

```env
VITE_API_URL=http://127.0.0.1:8000
```

### Start the frontend

```bash
npm run dev
```

The frontend will normally run at:

```text
http://localhost:5173
```

Use the local URL printed in the terminal if Vite selects another port.

## 7. Database

The application uses PostgreSQL.

The deployed application uses Neon PostgreSQL as its cloud database.

Database connection is configured through the `DATABASE_URL` environment variable.

SQLAlchemy is used to communicate with the database.

## 8. Demo Login Accounts

The following demo accounts were configured for testing:

| Role | Email | Password |
|---|---|---|
| Principal | principal@school.com | Principal@123 |
| Teacher | teacher@school.com | Teacher@123 |
| Student | student@school.com | Student@123 |

These are demonstration credentials. Change them before using the system with real school data.

## 9. Authentication

The application uses JSON Web Tokens (JWT) for authentication.

Login API:

```text
POST /auth/login
```

Example request:

```json
{
  "email": "student@school.com",
  "password": "Student@123"
}
```

Successful authentication returns:

- Access token
- Token type
- User role

The frontend stores the access token in session storage and sends it with authenticated API requests.

## 10. Deployment

The project is deployed using Vercel.

### Frontend Deployment

- Platform: Vercel
- Project: `stundent-dashboard`
- Environment variable: `VITE_API_URL`

### Backend Deployment

- Platform: Vercel
- Project: `student-dashboard-x5id`
- Root directory: `backend`

### Backend Environment Variables

Configure these in Vercel:

```env
DATABASE_URL=your_neon_database_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Production URLs

Frontend:

https://stundent-dashboard.vercel.app

Backend:

https://stundent-dashboard-x5id.vercel.app

Backend health:

https://stundent-dashboard-x5id.vercel.app/health

## 11. Git and GitHub Workflow

Initialize the repository:

```bash
git init
```

Check modified files:

```bash
git status
```

Add changes:

```bash
git add .
```

Commit changes:

```bash
git commit -m "describe your changes"
```

Push changes:

```bash
git push origin main
```

GitHub repository:

https://github.com/mukeshdhoni1030-cloud/stundent_Dashboard

## 12. Important Security Practices

- Never commit `.env` files.
- Never expose database passwords.
- Use strong secret keys.
- Protect APIs using authentication and role-based authorization.
- Validate all incoming API requests.
- Back up the database regularly.
- Confirm destructive operations before permanently deleting records.

## 13. Project Status

The application has been deployed to Vercel with Neon PostgreSQL.

The following have been verified:

- Frontend deployment
- Backend deployment
- Cloud database connection
- API authentication through FastAPI documentation
- Student login API
- Frontend-to-backend API configuration

Additional testing of Principal, Teacher, and Student features should be completed before production use.

---

**Project:** Student Dashboard – School Management System  
**Frontend:** React + Vite  
**Backend:** Python FastAPI  
**Database:** PostgreSQL / Neon  
**Hosting:** Vercel  
**Repository:** https://github.com/mukeshdhoni1030-cloud/stundent_Dashboard