# CareDesk — Smart OPD & Clinic Management SaaS

## Overview
Multi-tenant Hospital/Clinic Management System built on Zoho Catalyst.
Each clinic is a tenant with isolated data. Supports patient booking, queue management,
consultations, prescriptions, feedback with AI sentiment analysis.

---

## Tech Stack
- **Backend:** Python 3.9 (Catalyst Advanced I/O Function, Flask)
- **Frontend:** React 18 + Vite + Tailwind CSS
- **Database:** Catalyst Data Store (Relational) + ZCQL
- **Hosting:** Catalyst Slate (React) + Serverless Functions
- **AI:** Zia Text Analytics (sentiment), Zia OCR
- **SDK:** zcatalyst-sdk-python 1.1.0

---

## Project Structure

```
MediQ/
├── catalyst.json                          # Catalyst project config
├── .catalystrc                            # Catalyst RC file
├── ARCHITECTURE.md                        # This file
│
├── functions/
│   └── ragnar_hackathon_alok_swapnil_function/
│       ├── main.py                        # Entry point — request router
│       ├── catalyst-config.json           # Function deployment config
│       ├── requirements.txt               # Python dependencies
│       │
│       ├── routes/                        # API route handlers
│       │   ├── __init__.py
│       │   ├── clinic_routes.py           # /api/clinics/*
│       │   ├── doctor_routes.py           # /api/doctors/*
│       │   ├── patient_routes.py          # /api/patients/*
│       │   ├── appointment_routes.py      # /api/appointments/*
│       │   ├── prescription_routes.py     # /api/prescriptions/*
│       │   ├── public_routes.py           # /api/public/* (no auth)
│       │   └── dashboard_routes.py        # /api/dashboard/*
│       │
│       ├── services/                      # Business logic & integrations
│       │   ├── __init__.py
│       │   ├── auth_service.py            # Multi-tenant auth + clinic_id resolution
│       │   ├── mail_service.py            # Email sending (Catalyst Mail)
│       │   ├── cache_service.py           # Queue state caching (Catalyst Cache)
│       │   └── zia_service.py             # Zia Text Analytics & OCR
│       │
│       └── utils/                         # Shared utilities
│           ├── __init__.py
│           ├── response.py                # JSON response helpers
│           └── constants.py               # Table names, status enums, config
│
└── caredesk-client/                       # React + Vite (Slate)
    ├── index.html                         # Entry HTML (Catalyst SDK scripts)
    ├── package.json
    ├── vite.config.js                     # Vite + Tailwind config
    ├── .catalyst/
    │   └── slate-config.toml
    │
    └── src/
        ├── main.jsx                       # React entry + Router
        ├── App.jsx                        # Root component
        ├── index.css                      # Tailwind directives + global styles
        │
        ├── api/
        │   └── index.js                   # API helper (fetchAPI with Catalyst auth)
        │
        ├── layouts/
        │   └── DashboardLayout.jsx        # Sidebar + Header wrapper
        │
        ├── pages/
        │   ├── LoginPage.jsx              # Catalyst embedded auth
        │   ├── DashboardPage.jsx          # Stats overview
        │   ├── DoctorsPage.jsx            # Manage doctors (CRUD)
        │   ├── PatientsPage.jsx           # Patient registry + search
        │   ├── AppointmentsPage.jsx       # Today's appointments
        │   ├── QueuePage.jsx              # Live queue management
        │   ├── ConsultationPage.jsx       # Doctor writes prescription
        │   ├── PrescriptionViewPage.jsx   # View/print prescription
        │   ├── FeedbackPage.jsx           # View feedback + sentiment
        │   ├── SettingsPage.jsx           # Clinic settings, invite users
        │   └── public/
        │       ├── BookingPage.jsx        # Patient self-service booking
        │       ├── QueueDisplayPage.jsx   # Waiting room TV display
        │       └── FeedbackFormPage.jsx   # Patient submits feedback
        │
        ├── components/
        │   ├── Sidebar.jsx                # Navigation sidebar
        │   ├── Header.jsx                 # Top bar
        │   ├── StatsCard.jsx              # Dashboard stat card
        │   ├── QueueCard.jsx              # Patient queue card
        │   ├── AppointmentRow.jsx         # Table row
        │   ├── Modal.jsx                  # Reusable modal
        │   ├── LoadingSpinner.jsx         # Loading indicator
        │   └── StatusBadge.jsx            # Color-coded status badge
        │
        └── utils/
            └── constants.js               # API base URL, colors, enums
```

---

## Database Schema (Catalyst Data Store)

### Table 1: Clinics (Tenant Table)
| Column         | Type   | Description                          |
|----------------|--------|--------------------------------------|
| ROWID          | auto   | Primary key                          |
| name           | TEXT   | Clinic name                          |
| slug           | TEXT   | URL slug (unique, e.g. "apollo-delhi") |
| address        | TEXT   | Full address                         |
| phone          | TEXT   | Contact number                       |
| email          | TEXT   | Clinic email                         |
| admin_user_id  | TEXT   | Catalyst user ID of clinic owner     |
| logo_url       | TEXT   | Logo file URL (Stratus)              |
| CREATEDTIME    | auto   | Created timestamp                    |

### Table 2: Doctors
| Column         | Type   | Description                          |
|----------------|--------|--------------------------------------|
| ROWID          | auto   | Primary key                          |
| clinic_id      | TEXT   | FK → Clinics.ROWID (tenant isolation)|
| name           | TEXT   | Doctor's full name                   |
| specialty      | TEXT   | e.g., "Cardiology", "General"        |
| email          | TEXT   | Doctor's email                       |
| phone          | TEXT   | Phone number                         |
| available_from | TEXT   | Start time "09:00"                   |
| available_to   | TEXT   | End time "17:00"                     |
| consultation_fee | TEXT | Fee amount                           |
| status         | TEXT   | "active" / "inactive"                |

### Table 3: Patients
| Column          | Type   | Description                         |
|-----------------|--------|-------------------------------------|
| ROWID           | auto   | Primary key                         |
| clinic_id       | TEXT   | FK → Clinics.ROWID                  |
| name            | TEXT   | Patient full name                   |
| phone           | TEXT   | Phone (unique per clinic)           |
| email           | TEXT   | Email                               |
| age             | TEXT   | Age                                 |
| gender          | TEXT   | "Male" / "Female" / "Other"         |
| blood_group     | TEXT   | Blood group                         |
| medical_history | TEXT   | Notes / chronic conditions          |

### Table 4: Appointments
| Column             | Type   | Description                        |
|--------------------|--------|------------------------------------|
| ROWID              | auto   | Primary key                        |
| clinic_id          | TEXT   | FK → Clinics.ROWID                 |
| doctor_id          | TEXT   | FK → Doctors.ROWID                 |
| patient_id         | TEXT   | FK → Patients.ROWID                |
| appointment_date   | TEXT   | Date "YYYY-MM-DD"                  |
| appointment_time   | TEXT   | Time "HH:MM"                      |
| status             | TEXT   | booked/in-queue/in-consultation/completed/cancelled |
| token_number       | TEXT   | Queue token "A-001"                |
| notes              | TEXT   | Booking notes                      |
| feedback_score     | TEXT   | 1-5 star rating                    |
| feedback_text      | TEXT   | Patient feedback text              |
| feedback_sentiment | TEXT   | positive/negative/neutral (Zia)    |

### Table 5: Prescriptions
| Column           | Type   | Description                         |
|------------------|--------|-------------------------------------|
| ROWID            | auto   | Primary key                         |
| clinic_id        | TEXT   | FK → Clinics.ROWID                  |
| appointment_id   | TEXT   | FK → Appointments.ROWID             |
| doctor_id        | TEXT   | FK → Doctors.ROWID                  |
| patient_id       | TEXT   | FK → Patients.ROWID                 |
| diagnosis        | TEXT   | Diagnosis description               |
| medicines        | TEXT   | JSON string [{name, dosage, duration, instructions}] |
| advice           | TEXT   | Doctor's advice / instructions      |
| follow_up_date   | TEXT   | Follow-up date "YYYY-MM-DD"         |
| prescription_url | TEXT   | PDF URL (Stratus)                   |

---

## API Routes

### Authenticated Routes (require Catalyst auth token)

#### Clinics
| Method | Path               | Handler                    | Description              |
|--------|--------------------|----------------------------|--------------------------|
| POST   | /api/clinics       | clinic_routes.create       | Register new clinic      |
| GET    | /api/clinics/me    | clinic_routes.get_mine     | Get my clinic details    |
| PUT    | /api/clinics/me    | clinic_routes.update_mine  | Update my clinic         |

#### Doctors
| Method | Path               | Handler                    | Description              |
|--------|--------------------|----------------------------|--------------------------|
| GET    | /api/doctors       | doctor_routes.list_all     | List clinic's doctors    |
| POST   | /api/doctors       | doctor_routes.create       | Add doctor               |
| PUT    | /api/doctors/:id   | doctor_routes.update       | Update doctor            |
| DELETE | /api/doctors/:id   | doctor_routes.delete       | Remove doctor            |

#### Patients
| Method | Path                     | Handler                      | Description            |
|--------|--------------------------|------------------------------|------------------------|
| GET    | /api/patients            | patient_routes.list_all      | List clinic's patients |
| POST   | /api/patients            | patient_routes.create        | Register patient       |
| GET    | /api/patients/:id        | patient_routes.get_one       | Get patient detail     |
| PUT    | /api/patients/:id        | patient_routes.update        | Update patient         |
| GET    | /api/patients/search     | patient_routes.search        | Search patients (?q=)  |

#### Appointments
| Method | Path                           | Handler                          | Description              |
|--------|--------------------------------|----------------------------------|--------------------------|
| GET    | /api/appointments              | appointment_routes.list_today    | Today's appointments     |
| POST   | /api/appointments              | appointment_routes.create        | Book appointment         |
| PUT    | /api/appointments/:id          | appointment_routes.update        | Update status            |
| GET    | /api/appointments/queue        | appointment_routes.get_queue     | Live queue               |

#### Prescriptions
| Method | Path                           | Handler                          | Description              |
|--------|--------------------------------|----------------------------------|--------------------------|
| POST   | /api/prescriptions             | prescription_routes.create       | Create prescription      |
| GET    | /api/prescriptions/:id         | prescription_routes.get_one      | Get prescription         |
| GET    | /api/prescriptions/patient/:id | prescription_routes.by_patient   | Patient's history        |

#### Dashboard
| Method | Path                  | Handler                    | Description              |
|--------|-----------------------|----------------------------|--------------------------|
| GET    | /api/dashboard/stats  | dashboard_routes.get_stats | Today's statistics       |

### Public Routes (no auth required)

| Method | Path                              | Handler                        | Description              |
|--------|-----------------------------------|--------------------------------|--------------------------|
| GET    | /api/public/clinic/:slug          | public_routes.get_clinic       | Clinic info + doctors    |
| POST   | /api/public/book                  | public_routes.book_appointment | Patient self-book        |
| GET    | /api/public/queue/:slug           | public_routes.get_queue        | Live queue status        |
| POST   | /api/public/feedback/:appt_id     | public_routes.submit_feedback  | Submit feedback + Zia    |

---

## Multi-Tenancy Architecture

```
Request → Extract Auth Token → Get User ID → Lookup clinic_id from Clinics table
→ ALL subsequent queries filter by WHERE clinic_id = '{clinic_id}'
```

- Every table has a `clinic_id` column
- `auth_service.get_clinic_id(app)` is called at the start of every authenticated route
- Public routes use `slug` to identify the clinic instead
- Users are invited to a clinic's org via Catalyst User Management

---

## Catalyst Services Integration

| #  | Service              | Where Used                                    | Priority |
|----|----------------------|-----------------------------------------------|----------|
| 1  | Auth / User Mgmt     | Login, tenant isolation, invite users         | P0       |
| 2  | Data Store + ZCQL    | All 5 tables, complex queries                 | P0       |
| 3  | Functions (Adv I/O)  | Python backend API                            | P0       |
| 4  | Slate                | React frontend hosting                        | P0       |
| 5  | Cache                | Live queue state, dashboard metrics           | P1       |
| 6  | Mail                 | Appointment confirmations, prescriptions      | P1       |
| 7  | Stratus              | Prescription PDFs, clinic logos                | P1       |
| 8  | Search               | Patient search                                | P1       |
| 9  | Zia Text Analytics   | Feedback sentiment analysis                   | P1       |
| 10 | Job Scheduling       | Follow-up reminders, daily                     | P2       |
| 13 | Push Notifications   | "Your turn is next!" alerts                   | P2       |
| 14 | SmartBrowz           | Generate prescription PDFs                    | P2       |
| 15 | ConvoKraft           | Patient chatbot on booking page               | P2       |
| 16 | Zia OCR              | Scan old prescriptions                        | P3       |
| 17 | NoSQL                | Flexible consultation notes                   | P3       |

---

## Frontend Pages & Routing

| Path                          | Component              | Auth? | Description                  |
|-------------------------------|------------------------|-------|------------------------------|
| /                             | LoginPage              | No    | Catalyst embedded login      |
| /dashboard                    | DashboardPage          | Yes   | Stats + overview             |
| /doctors                      | DoctorsPage            | Yes   | Doctor CRUD                  |
| /patients                     | PatientsPage           | Yes   | Patient registry + search    |
| /appointments                 | AppointmentsPage       | Yes   | Today's appointments         |
| /queue                        | QueuePage              | Yes   | Receptionist queue mgmt      |
| /consultation/:appointmentId  | ConsultationPage       | Yes   | Doctor writes prescription   |
| /prescription/:id             | PrescriptionViewPage   | Yes   | View/print prescription      |
| /feedback                     | FeedbackPage           | Yes   | All feedback + sentiment     |
| /settings                     | SettingsPage           | Yes   | Clinic config + invite       |
| /book/:slug                   | BookingPage            | No    | Public patient booking       |
| /queue-display/:slug          | QueueDisplayPage       | No    | Public waiting room display  |
| /feedback-form/:appointmentId | FeedbackFormPage       | No    | Public feedback submission   |

---

## Demo Flow
1. Clinic A admin signs up → registers clinic "Apollo Delhi"
2. Adds 2 doctors (Dr. Shah - Cardiology, Dr. Patel - General)
3. Patient visits /book/apollo-delhi → books with Dr. Shah
4. Patient gets confirmation email (Mail)
5. Patient arrives → receptionist adds to queue
6. Queue display shows live positions (public page)
7. Doctor calls next → writes prescription
8. Prescription PDF emailed to patient
9. Patient submits feedback → Zia detects sentiment
10. Dashboard shows today's stats
11. Switch to Clinic B → completely different data (multi-tenancy proof)
