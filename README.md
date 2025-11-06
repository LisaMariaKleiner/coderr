# Coderr - Freelancer Platform

Ein Full-Stack Projekt mit Django REST Framework Backend und Vanilla JavaScript Frontend.

## 📁 Projekt-Struktur (Monorepo)

```
project.Coderr/
├── frontend/                 # Vanilla JS Frontend
│   ├── index.html
│   ├── scripts/
│   ├── styles/
│   └── shared/
│
└── backend/                  # Django REST API
    ├── manage.py
    ├── requirements.txt
    ├── config/              # Django Konfiguration
    ├── apps/                # Django Apps
    │   ├── authentication/  # Login & Registration
    │   ├── users/          # User & Profile Management
    │   ├── offers/         # Angebote (CRUD)
    │   ├── orders/         # Bestellungen
    │   └── reviews/        # Bewertungen
    ├── shared/             # Gemeinsame Utilities
    ├── media/              # Upload Files
    └── static/             # Static Backend Files
```

## 🚀 Backend Setup

### 1. Virtual Environment erstellen

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate
```

### 2. Dependencies installieren

```powershell
pip install -r requirements.txt
```

### 3. Environment Variables

```powershell
cp .env.example .env
# Bearbeite .env und setze SECRET_KEY
```

### 4. Datenbank migrieren

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Superuser erstellen (optional)

```powershell
python manage.py createsuperuser
```

### 6. Server starten

```powershell
python manage.py runserver
```

Backend läuft auf: `http://127.0.0.1:8000/`
Admin Panel: `http://127.0.0.1:8000/admin/`

## 🎨 Frontend Setup

Das Frontend benötigt einen einfachen HTTP Server:

### Option 1: Live Server (VS Code Extension)

- Installiere "Live Server" Extension
- Rechtsklick auf `frontend/index.html` → "Open with Live Server"

### Option 2: Python HTTP Server

```powershell
cd frontend
python -m http.server 5500
```

Frontend läuft auf: `http://127.0.0.1:5500/`

## 📡 API Endpoints

### Authentication

- `POST /api/login/` - Login
- `POST /api/registration/` - Registration
- `POST /api/logout/` - Logout (Token Required)

### Users & Profiles

- `GET/PUT/PATCH /api/profiles/business/` - Business Profile CRUD
- `GET/PUT/PATCH /api/profiles/customer/` - Customer Profile CRUD
- `GET /api/profiles/business/me/` - Eigenes Business Profil
- `GET /api/profiles/customer/me/` - Eigenes Customer Profil

### Offers

- `GET /api/offers/` - Liste aller Angebote
- `POST /api/offers/` - Neues Angebot erstellen (Business only)
- `GET /api/offers/{id}/` - Einzelnes Angebot
- `PUT/PATCH /api/offers/{id}/` - Angebot bearbeiten (Owner only)
- `DELETE /api/offers/{id}/` - Angebot löschen (Owner only)
- `GET /api/offers/my_offers/` - Eigene Angebote

### Orders

- `GET /api/orders/` - Liste aller Orders (gefiltert nach User)
- `POST /api/orders/` - Neue Bestellung erstellen
- `GET /api/orders/{id}/` - Einzelne Order
- `PATCH /api/orders/{id}/update_status/` - Status aktualisieren (Business only)

### Reviews

- `GET /api/reviews/` - Liste aller Reviews
- `POST /api/reviews/` - Neue Review erstellen (Customer only)
- `GET /api/reviews/{id}/` - Einzelne Review
- `PUT/PATCH /api/reviews/{id}/` - Review bearbeiten (Owner only)
- `DELETE /api/reviews/{id}/` - Review löschen (Owner only)

## 🔐 Authentication

Das Backend nutzt Token Authentication:

```javascript
// Login
fetch("http://127.0.0.1:8000/api/login/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ username: "user", password: "pass" }),
})
  .then((res) => res.json())
  .then((data) => {
    localStorage.setItem("auth-token", data.token);
  });

// API Calls mit Token
fetch("http://127.0.0.1:8000/api/offers/", {
  headers: {
    Authorization: `Token ${localStorage.getItem("auth-token")}`,
  },
});
```

## 🛠️ Nützliche Commands

```powershell
# Neue Migrationen erstellen
python manage.py makemigrations

# Migrationen anwenden
python manage.py migrate

# Shell öffnen
python manage.py shell

# Tests ausführen
python manage.py test

# Static Files sammeln (für Production)
python manage.py collectstatic
```

## 📦 Technologie-Stack

### Backend

- Django 5.0
- Django REST Framework 3.14
- Token Authentication
- CORS Headers
- SQLite (Development) / PostgreSQL (Production ready)

### Frontend

- Vanilla JavaScript (ES6+)
- CSS3
- Fetch API

## 🔧 CORS Konfiguration

In `backend/config/settings.py` sind folgende Origins erlaubt:

- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:5500`
- `http://127.0.0.1:5500`

Für andere Ports/URLs: `CORS_ALLOWED_ORIGINS` in `settings.py` anpassen.

## 📝 Development Workflow

1. **Backend zuerst starten**: `python manage.py runserver`
2. **Frontend starten**: Live Server oder HTTP Server
3. **API im Browser testen**: `http://127.0.0.1:8000/api/`
4. **Frontend testen**: `http://127.0.0.1:5500/`

## 🚧 Produktions-Deployment

### Backend (Django)

- `DEBUG = False` setzen
- Secret Key über Environment Variable laden
- PostgreSQL/MySQL Database einrichten
- Gunicorn/uWSGI als WSGI Server
- Nginx als Reverse Proxy
- HTTPS einrichten

### Frontend

- Static Files auf CDN/Webserver
- API_BASE_URL in `shared/scripts/config.js` auf Production URL anpassen

## 📚 Weitere Dokumentation

- [Django Docs](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [API Browser](http://127.0.0.1:8000/api/) (wenn Backend läuft)

## 🤝 Mitarbeit

Branches erstellen für neue Features:

```powershell
git checkout -b feature/neue-funktion
```

## 📄 Lizenz

Siehe LICENSE.md
