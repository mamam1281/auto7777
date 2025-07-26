# Casino-Club F2P Backend

This is the backend API for the Casino-Club F2P application, built with FastAPI and SQLAlchemy.

## Features

- Admin Dashboard API
- User Management
- Activity Tracking
- Reward System

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create test data (optional):

```bash
python create_test_data.py
```

4. Run the application:

```bash
python run_app.py
```

The API will be available at http://localhost:8000.

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── models/         # SQLAlchemy models
│   ├── routers/        # API routes
│   ├── schemas/        # Pydantic schemas
│   ├── database.py     # Database configuration
│   └── main.py         # FastAPI application
├── create_test_data.py # Script to create test data
├── requirements.txt    # Python dependencies
└── run_app.py          # Application entry point
```

## Admin API Endpoints

- `GET /admin/users` - List all users
- `GET /admin/users/{user_id}` - Get user details
- `GET /admin/activities` - List user activities
- `POST /admin/rewards` - Give reward to user
