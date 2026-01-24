# Coderr – Freelancer Plattform

Vollständiges Full-Stack-Projekt mit Django REST Framework (Backend) und Vanilla JavaScript (Frontend).

## 📁 Projektstruktur (Stand 2026)

```
project.Coderr/
├── authentication_app/       # Registrierung, Login
│   └── api/
├── base_info_app/            # Plattform-Informationen
│   └── api/
├── core/                     # Django-Konfiguration & Settings
├── frontend/                 # Vanilla JS Frontend
│   ├── *.html                # Hauptseiten
│   ├── scripts/              # Seitenspezifische JS
│   ├── styles/               # CSS für Seiten
│   └── shared/               # Gemeinsame Scripts & Styles
│       ├── scripts/          # z.B. api.js, auth.js, config.js
│       └── styles/
├── manage.py                 # Django Management
├── media/                    # Hochgeladene Dateien (z.B. Profilbilder)
│   └── profiles/customer/
├── offers_app/               # Angebote (Offers)
│   └── api/
├── orders_app/               # Bestellungen (Orders)
│   └── api/
├── profiles_app/             # Nutzer- & Profilverwaltung
│   └── api/
├── reviews_app/              # Bewertungen
│   └── api/
├── requirements.txt          # Python-Abhängigkeiten
├── static/                   # Statische Backend-Dateien
└── db.sqlite3                # SQLite-DB (dev)
```

## 🚀 Backend-Setup (Django) – Schritt für Schritt (Windows, Linux, Mac)

### 1. Python installieren

- **Windows:**
  - Lade Python von https://www.python.org/downloads/ herunter und installiere es.
  - Achte darauf, beim Setup „Add Python to PATH“ auszuwählen!
- **Linux/Mac:**
  - Meist ist Python schon installiert. Prüfe mit:
    ```bash
    python3 --version
    ```
  - Falls nicht, installiere es z.B. mit `sudo apt install python3` (Linux) oder `brew install python` (Mac).

### 2. Virtuelle Umgebung anlegen

Im Projektordner im Terminal/PowerShell:

- **Windows:**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate
  ```
- **Linux/Mac:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

**Hinweis:**

- Nach Aktivierung steht links im Terminal `(venv)`.
- Falls „python nicht gefunden“: Starte Terminal neu oder prüfe, ob Python installiert ist.

### 3. Abhängigkeiten installieren

Im aktivierten venv:

- **Windows:**
  ```powershell
  pip install -r requirements.txt
  ```
- **Linux/Mac:**
  ```bash
  pip install -r requirements.txt
  ```

**Fehler?**

- Prüfe, ob du im richtigen Ordner bist und die venv aktiv ist.

### 4. (Optional) Umgebungsvariablen setzen

- Lege eine Datei `.env` im Projektordner an (z.B. für SECRET_KEY, DEBUG, ALLOWED_HOSTS).
- Beispiel-Inhalt:
  ```env
  SECRET_KEY=dein-geheimer-key
  DEBUG=True
  ALLOWED_HOSTS=localhost,127.0.0.1
  ```

### 5. Migrationen anwenden (Datenbank vorbereiten)

- **Windows:**
  ```powershell
  python manage.py makemigrations
  python manage.py migrate
  ```
- **Linux/Mac:**
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

### 6. Superuser anlegen (optional, für Admin-Login)

- **Windows:**
  ```powershell
  python manage.py createsuperuser
  ```
- **Linux/Mac:**
  ```bash
  python manage.py createsuperuser
  ```

Folge den Anweisungen im Terminal (Benutzername, E-Mail, Passwort).

### 7. Server starten

- **Windows:**
  ```powershell
  python manage.py runserver
  ```
- **Linux/Mac:**
  ```bash
  python manage.py runserver
  ```

**Erfolg:**

- Im Terminal steht: „Starting development server at http://127.0.0.1:8000/“
- Öffne im Browser:
  - Backend: http://127.0.0.1:8000/
  - Admin: http://127.0.0.1:8000/admin/

### 6. Server starten

```powershell
python manage.py runserver
```

Backend: `http://127.0.0.1:8000/`
Admin Panel: `http://127.0.0.1:8000/admin/`

## 📡 API-Endpoints (Auszug)

**Authentication**

- `POST   /api/login/` – Login
- `POST   /api/registration/` – Registrierung
- `POST   /api/logout/` – Logout (Token)

**Profile**

- `GET/PUT/PATCH /api/profiles/business/` – Business-Profil CRUD
- `GET/PUT/PATCH /api/profiles/customer/` – Customer-Profil CRUD
- `GET /api/profiles/business/me/` – Eigenes Business-Profil
- `GET /api/profiles/customer/me/` – Eigenes Customer-Profil

**Offers**

- `GET    /api/offers/` – Alle Angebote (Filter, Suche, Pagination)
- `POST   /api/offers/` – Neues Angebot (nur Business)
- `GET    /api/offers/{id}/` – Einzelnes Angebot
- `PUT/PATCH /api/offers/{id}/` – Angebot bearbeiten (Owner)
- `DELETE /api/offers/{id}/` – Angebot löschen (Owner)
- `GET    /api/offers/my_offers/`– Eigene Angebote (Business)

**Orders**

- `GET    /api/orders/` – Bestellungen (User-Filter)
- `POST   /api/orders/` – Neue Bestellung
- `GET    /api/orders/{id}/` – Einzelne Bestellung
- `PATCH  /api/orders/{id}/update_status/` – Status ändern (Business)

**Reviews**

- `GET    /api/reviews/` – Alle Bewertungen
- `POST   /api/reviews/` – Neue Bewertung (Customer)
- `GET    /api/reviews/{id}/` – Einzelne Bewertung
- `PUT/PATCH /api/reviews/{id}/` – Bewertung bearbeiten (Owner)
- `DELETE /api/reviews/{id}/` – Bewertung löschen (Owner)

## 🛠️ Nützliche Kommandos

```powershell
# Migrationen erstellen
python manage.py makemigrations
# Migrationen anwenden
python manage.py migrate
# Shell öffnen
python manage.py shell
# Tests ausführen
python manage.py test
# Statische Dateien sammeln (Production)
python manage.py collectstatic
```

## 📦 Tech Stack

**Backend:**

- Django 5.0
- Django REST Framework 3.14
- Token Auth
- django-cors-headers, django-filter
- SQLite (dev) / PostgreSQL (prod-ready)

**Frontend:**

- Vanilla JavaScript (ES6+)
- CSS3
- Fetch API

## 🔧 CORS-Konfiguration

Erlaubte Origins in `core/settings.py`:

- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:5500`
- `http://127.0.0.1:5500`

Weitere Ports/URLs ggf. in `CORS_ALLOWED_ORIGINS` ergänzen.

## 📝 Entwicklungs-Workflow

1. Backend starten: `python manage.py runserver`
2. Frontend starten: Live Server/HTTP-Server im `frontend/`-Ordner (z.B. mit VSCode Extension)
3. API testen: http://127.0.0.1:8000/api/
4. Frontend testen: http://127.0.0.1:5500/

## 🚧 Deployment (Production)

**Backend:**

- `DEBUG = False` setzen
- SECRET_KEY als Umgebungsvariable
- PostgreSQL/MySQL einrichten
- Gunicorn/uWSGI + Nginx
- HTTPS aktivieren

**Frontend:**

- Statische Dateien auf Webserver/CDN
- `API_BASE_URL` in `frontend/shared/scripts/config.js` auf Produktiv-URL setzen

## 📚 Weitere Doku & Links

- [Django Doku](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [API-Browser](http://127.0.0.1:8000/api/) (wenn Backend läuft)
