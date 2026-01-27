# FastAPI Starter Template

A production-ready FastAPI starter template with modular architecture, essential developer tools, and environment-based configuration.

## Features

- 🚀 **FastAPI** - Modern, fast web framework for building APIs
- 🗃️ **SQLAlchemy** - SQL toolkit and Object-Relational Mapping (ORM)
- ✅ **Pydantic** - Data validation using Python type annotations
- 🔐 **JWT Authentication** - Secure authentication with JSON Web Tokens
- 🗄️ **PostgreSQL** - Production-ready database
- 📝 **Alembic** - Database migration tool
- 🧪 **Pytest** - Testing framework
- 🐳 **Docker** - Containerization support
- 📖 **OpenAPI/Swagger** - Automatic API documentation
- ⚡ **Redis** - Caching and session storage
- 🔧 **Pre-commit hooks** - Code quality assurance
- 📊 **Logging** - Structured logging configuration
- 🌍 **CORS** - Cross-Origin Resource Sharing support

## Project Structure

```
FastApiStart/
├── app/                          # Main application package
│   ├── api/                      # API layer
│   │   ├── v1/                   # API version 1
│   │   │   ├── endpoints/        # API endpoints
│   │   │   └── api.py           # API router configuration
│   │   ├── deps.py              # Dependencies
│   │   └── management_deps.py   # Management dependencies
│   ├── core/                    # Core functionality
│   │   ├── config.py           # Configuration settings
│   │   ├── security.py         # Security utilities
│   │   ├── permissions.py      # Permission system
│   │   ├── multitenancy.py     # Multi-tenant support
│   │   └── logging.py          # Logging configuration
│   ├── crud/                   # CRUD operations
│   ├── db/                     # Database configuration
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── wathq/                  # External API integrations
│   └── main.py                 # FastAPI application
├── alembic/                    # Database migrations
├── docs/                       # Documentation
├── logs/                       # Application logs
├── requirements/               # Dependencies
├── scripts/                    # Utility scripts
├── setup/                      # Setup and deployment scripts
├── tests/                      # Test suite
├── .env                        # Environment variables
├── .env.example               # Environment template
├── alembic.ini                # Alembic configuration
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FastApiStart
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/requirements-dev.txt
   ```

4. **Set up database**
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Create initial superuser
   python setup/create_superuser.py
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and adjust the values:

```bash
# Environment
ENVIRONMENT=development

# Security
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## Features Overview

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Multi-tenant support
- Management user system

### API Structure
- RESTful API design
- Automatic OpenAPI documentation
- Request/response validation
- Error handling

### Database
- Async SQLAlchemy ORM
- Alembic migrations
- Multi-tenant architecture
- Connection pooling

### External Integrations
- WATHQ API integration
- Commercial registration services
- Real estate services
- Employee verification

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
# Format code
ruff format .

# Lint code
ruff check .
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh token

### Management
- `POST /api/v1/management/auth/login` - Management login
- `GET /api/v1/management/users` - List users
- `POST /api/v1/management/users` - Create user

### Services
- `GET /api/v1/services` - List available services
- `POST /api/v1/services` - Create service

### Health Check
- `GET /api/v1/health` - Application health status

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request


# Check database status
python setup/check_db_status.py

# Clean migration (when foreign keys exist)
python setup/migrate_refresh_db.py --mode reset --test-data --force

# Regular migration (preserves structure)
python setup/migrate_refresh_db.py --mode clean --test-data


Summary
✅ Database Migration Issue Resolved!

What was fixed:
Foreign Key Constraints - Updated the cleaning order to handle junction tables (role_permissions, user_roles) before their parent tables
CASCADE Deletion - Added fallback to TRUNCATE CASCADE when foreign key constraints prevent normal deletion
Error Handling - Improved error handling for constraint violations
Current Database Status:
6 WATHQ Services loaded and active
10 Permissions configured
3 Roles defined (WATHQ Admin, Manager, User)
4 Tenants including test organizations
3 Test Users with different access levels
New Tools Created:
setup/check_db_status.py
 - Quick database health check script
Quick Commands:
bash
# Check database status
python setup/check_db_status.py

# Clean migration (when foreign keys exist)
python setup/migrate_refresh_db.py --mode reset --test-data --force

# Regular migration (preserves structure)
python setup/migrate_refresh_db.py --mode clean --test-data
The migration script now properly handles foreign key constraints by:

Cleaning junction tables before parent tables
Using TRUNCATE CASCADE as a fallback for stubborn constraints
Maintaining proper dependency order for all WATHQ tables
Your database is now fully refreshed with clean seed data and ready for API testing!


# install ubuntu lib 
apt-get install wkhtmltopdf
## License

This project is licensed under the MIT License.

