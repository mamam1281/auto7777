# Casino-Club F2P Project Setup Guide

This guide will help you set up the Casino-Club F2P project environment using Docker Compose. The project consists of the following components:

- **Backend API Server**: FastAPI + Python
- **Frontend Web App**: Next.js + React
- **Database**: PostgreSQL
- **Cache**: Redis
- **Message Broker**: Kafka (with Zookeeper)
- **Background Processing**: Celery (worker and beat)

## Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)
- PowerShell (for Windows) or Bash (for Linux/Mac)

## Project Structure

```
cc-webapp/
├── backend/              # FastAPI backend application
│   ├── app/              # Main application code
│   ├── alembic/          # Database migrations
│   ├── scripts/          # Utility scripts
│   ├── tests/            # Backend tests
│   └── Dockerfile        # Backend Docker configuration
├── frontend/             # Next.js frontend application
│   ├── app/              # Application routes
│   ├── components/       # React components
│   ├── pages/            # Next.js pages
│   ├── public/           # Static assets
│   └── Dockerfile        # Frontend Docker configuration
├── docker-compose.yml    # Main Docker Compose configuration
└── docker-compose.override.yml # Development-specific overrides
```

## Quick Start

1. Clone the repository and navigate to the project directory
2. Run the Docker environment:

```powershell
# On Windows
./docker-simple.ps1 start

# On Linux/Mac
./dev.sh start
```

3. Access the applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Docker Environment Management

We provide a PowerShell script (`docker-simple.ps1`) to easily manage the Docker environment:

```powershell
# Start all containers
./docker-simple.ps1 start

# View container status
./docker-simple.ps1 status

# View logs
./docker-simple.ps1 logs        # All logs
./docker-simple.ps1 backend     # Backend logs only
./docker-simple.ps1 frontend    # Frontend logs only
./docker-simple.ps1 db          # Database logs only

# Stop all containers
./docker-simple.ps1 stop
```

## Environment Configuration

The application is configured via environment variables. Default values are set in the Docker Compose files, but you can override them by creating a `.env` file in the project root:

```env
# Database
DB_NAME=cc_webapp
DB_USER=cc_user
DB_PASSWORD=cc_password

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Application Settings
APP_ENV=development
DEBUG=true
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Initial Cyber Token Amount
INITIAL_CYBER_TOKENS=200
```

## Core Features

The Casino-Club F2P application provides the following key features:

1. **User Authentication**: JWT-based authentication system with invite codes
2. **Game Core**: Multiple mini-games including Slot Machine, Gacha, and more
3. **Freemium Economy**: Virtual currencies and shop system
4. **Battle-Pass System**: Progression-based rewards
5. **Data-Driven Personalization**: User segmentation and personalized content

## Development Workflow

1. **Backend Development**:
   - Code is in Python using FastAPI framework
   - Changes to backend code are hot-reloaded (no container restart needed)
   - Database schema changes require Alembic migrations

2. **Frontend Development**:
   - Code is in TypeScript/JavaScript using Next.js and React
   - UI styling with Tailwind CSS and animations with Framer Motion
   - Changes to frontend code are hot-reloaded

3. **Database Access**:
   - Connect to PostgreSQL: `./docker-simple.ps1 db`
   - Direct connection: localhost:5432 with credentials from environment variables

4. **Testing**:
   - Backend tests with pytest
   - Frontend tests with Jest and React Testing Library

## Troubleshooting

- **Container Won't Start**: Check Docker logs for errors
- **Database Connection Issues**: Ensure PostgreSQL container is running and healthy
- **Backend API Errors**: Check backend logs for Python exceptions
- **Frontend Build Failures**: Check frontend logs for compilation errors

## Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Next.js Documentation: https://nextjs.org/docs
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Docker Compose Documentation: https://docs.docker.com/compose/
