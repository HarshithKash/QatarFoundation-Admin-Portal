# QatarFoundation Admin Portal

A full-stack admin dashboard for the **CertifyMe / Sky Foundation Universal Skills Passport** platform.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| Database | SQLite (via SQLAlchemy) |
| Auth | Werkzeug password hashing + Flask sessions |
| Frontend | Pre-built Admin UI (HTML / CSS / JS) |

---

## Features

### Authentication
- Admin Sign Up (full name, email, password)
- Admin Login with session handling (Remember Me)
- Forgot Password (token generated, 1-hour expiry, log only)
- Captcha validation on all auth forms

### Opportunity Management (Full CRUD)
- Create, Read, Update, Delete opportunities
- All data persisted in SQLite database
- Each admin sees only their own opportunities
- No hardcoded or local-storage data

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/signup | Register new admin |
| POST | /api/login | Login |
| POST | /api/logout | Logout |
| POST | /api/forgot-password | Request password reset |
| GET | /api/opportunities | Get all opportunities (auth required) |
| POST | /api/opportunities | Create opportunity (auth required) |
| GET | /api/opportunities/<id> | Get single opportunity |
| PUT | /api/opportunities/<id> | Update opportunity |
| DELETE | /api/opportunities/<id> | Delete opportunity |

---

## Original Repository
[https://github.com/Neerajvs32/Test1](https://github.com/Neerajvs32/Test1)
