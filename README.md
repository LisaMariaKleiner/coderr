# Coderr - Freelancer Platform

A full-stack project with Django REST Framework backend and Vanilla JavaScript frontend.

## 📁 Project Structure (Monorepo)

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
    ├── core/                # Django core config
    ├── authentication_app/  # Login & Registration
    ├── profiles_app/           # User & Profile Management
    ├── offers_app/          # Offers (CRUD)
    ├── orders_app/          # Orders
    ├── reviews_app/         # Reviews
    ├── platform_info_app/   # Platform Info
    ├── shared/              # Shared utilities
    ├── media/               # Uploaded files
    └── static/              # Static backend files
```

## 🚀 Backend Setup

### 1. Create virtual environment

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Environment variables

Copy `.env.example` to `.env` and set your `SECRET_KEY`.

### 4. Migrate database

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser (optional)

```powershell
python manage.py createsuperuser
```

### 6. Start server

```powershell
python manage.py runserver
```

Backend: `http://127.0.0.1:8000/`
Admin Panel: `http://127.0.0.1:8000/admin/`

## 🎨 Frontend Setup

You need a simple HTTP server for the frontend:

### Option 1: Live Server (VS Code Extension)

- Install "Live Server" extension
- Right-click `frontend/index.html` → "Open with Live Server"

### Option 2: Python HTTP Server

```powershell
cd frontend
python -m http.server 5500
```

Frontend: `http://127.0.0.1:5500/`

## 📡 API Endpoints

### Authentication

- `POST /api/login/` - Login
- `POST /api/registration/` - Registration
- `POST /api/logout/` - Logout (Token required)

### Users & Profiles

- `GET/PUT/PATCH /api/profiles/business/` - Business profile CRUD
- `GET/PUT/PATCH /api/profiles/customer/` - Customer profile CRUD
- `GET /api/profiles/business/me/` - Own business profile
- `GET /api/profiles/customer/me/` - Own customer profile

### Offers

- `GET /api/offers/` - List all offers
- `POST /api/offers/` - Create new offer (business only)
- `GET /api/offers/{id}/` - Single offer
- `PUT/PATCH /api/offers/{id}/` - Edit offer (owner only)
- `DELETE /api/offers/{id}/` - Delete offer (owner only)
- `GET /api/offers/my_offers/` - Own offers

### Orders

- `GET /api/orders/` - List all orders (filtered by user)
- `POST /api/orders/` - Create new order
- `GET /api/orders/{id}/` - Single order
- `PATCH /api/orders/{id}/update_status/` - Update status (business only)

### Reviews

- `GET /api/reviews/` - List all reviews
- `POST /api/reviews/` - Create new review (customer only)
- `GET /api/reviews/{id}/` - Single review
- `PUT/PATCH /api/reviews/{id}/` - Edit review (owner only)
- `DELETE /api/reviews/{id}/` - Delete review (owner only)

## 🔐 Authentication

The backend uses token authentication:

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

// API calls with token
fetch("http://127.0.0.1:8000/api/offers/", {
  headers: {
    Authorization: `Token ${localStorage.getItem("auth-token")}`,
  },
});
```

## 🛠️ Useful Commands

```powershell
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Open shell
python manage.py shell

# Run tests
python manage.py test

# Collect static files (for production)
python manage.py collectstatic
```

## 📦 Tech Stack

### Backend

- Django 5.0
- Django REST Framework 3.14
- Token Authentication
- CORS Headers
- SQLite (development) / PostgreSQL (production ready)

### Frontend

- Vanilla JavaScript (ES6+)
- CSS3
- Fetch API

## 🔧 CORS Configuration

Allowed origins in `backend/core/settings.py`:

- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:5500`
- `http://127.0.0.1:5500`

For other ports/URLs: adjust `CORS_ALLOWED_ORIGINS` in `settings.py`.

## 📝 Development Workflow

1. **Start backend first**: `python manage.py runserver`
2. **Start frontend**: Live Server or HTTP server
3. **Test API in browser**: `http://127.0.0.1:8000/api/`
4. **Test frontend**: `http://127.0.0.1:5500/`

## 🚧 Production Deployment

### Backend (Django)

- Set `DEBUG = False`
- Load secret key via environment variable
- Set up PostgreSQL/MySQL database
- Use Gunicorn/uWSGI as WSGI server
- Use Nginx as reverse proxy
- Enable HTTPS

### Frontend

- Host static files on CDN/web server
- Set `API_BASE_URL` in `shared/scripts/config.js` to production URL

## 📚 Further Documentation

- [Django Docs](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [API Browser](http://127.0.0.1:8000/api/) (when backend is running)
