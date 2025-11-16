# E-Commerce API

A multi-tenant e-commerce platform API built with Django REST Framework, featuring product management, order processing, and JWT authentication.

## Features

- 🔐 **JWT Authentication** - Secure token-based authentication
- 🏢 **Multi-tenant Architecture** - Company-based data isolation
- 📦 **Product Management** - CRUD operations for products with stock tracking
- 🛒 **Order Processing** - Create and manage orders with automatic stock decrementing
- 👥 **User Management** - Custom user model with role-based permissions
- 📊 **API Documentation** - Interactive Swagger UI and ReDoc
- 🐳 **Docker Support** - Fully containerized with Docker Compose
- 🔍 **Filtering & Search** - Built-in search and ordering capabilities

## Tech Stack

- **Backend**: Django 5.2.8, Django REST Framework 3.15.2
- **Database**: MySQL 8.0
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API Documentation**: drf-spectacular (OpenAPI 3)
- **Containerization**: Docker & Docker Compose

## Project Structure

```
ecommerce/
├── accounts/           # User authentication and management
├── companies/          # Company/tenant management
├── products/           # Product CRUD and inventory
├── orders/             # Order processing and management
├── ecommerce/          # Project settings and configuration
├── templates/          # HTML templates
├── staticfiles/        # Collected static files
├── docker-compose.yml  # Docker services configuration
├── Dockerfile          # Web container definition
├── requirements.txt    # Python dependencies
└── .env               # Environment variables (not in git)
```

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce
   ```

2. **Configure environment variables**
   
   The `.env` file is already created with default values:
   ```env
   DB_NAME=ecommerce_db
   DB_USER=ecommerce_user
   DB_PASSWORD=password
   DB_HOST=db
   DB_PORT=3306
   DEBUG=True
   SECRET_KEY=<your-secret-key>
   ```

3. **Start the containers**
   ```bash
   docker compose up --build -d
   ```

4. **Run migrations**
   ```bash
   docker exec ecommerce_web python manage.py migrate
   ```

5. **Collect static files**
   ```bash
   docker exec ecommerce_web python manage.py collectstatic --noinput
   ```

6. **Create a superuser**
   
   First create a company, then create a superuser:
   ```bash
   docker exec -it ecommerce_web python manage.py shell
   ```
   
   In the shell:
   ```python
   from companies.models import Company
   from accounts.models import User
   
   # Create a company
   company = Company.objects.create(name='Default Company')
   
   # Create superuser
   User.objects.create_superuser(
       email='admin@example.com',
       password='admin123',
       company=company
   )
   exit()
   ```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout (blacklist token)

### Products
- `GET /api/products/` - List all products (paginated, searchable)
- `POST /api/products/` - Create new product
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product
- `PATCH /api/products/{id}/` - Partial update
- `DELETE /api/products/{id}/` - Delete product

### Orders
- `GET /api/orders/` - List all orders
- `POST /api/orders/` - Create new order(s)
- `GET /api/orders/{id}/` - Get order details
- `PATCH /api/orders/{id}/` - Update order status

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. **Get tokens**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@example.com","password":"admin123"}'
   ```

2. **Use the access token** in subsequent requests:
   ```bash
   curl -X GET http://localhost:8000/api/products/ \
     -H "Authorization: Bearer <your-access-token>"
   ```

3. **Refresh token** when it expires:
   ```bash
   curl -X POST http://localhost:8000/api/auth/token/refresh/ \
     -H "Content-Type: application/json" \
     -d '{"refresh":"<your-refresh-token>"}'
   ```

## Using Swagger UI

1. Open http://localhost:8000/api/docs/
2. Click **Authorize** button (top right)
3. Enter: `Bearer <your-access-token>`
4. Click **Authorize** then **Close**
5. Now you can test all endpoints interactively

## Development Commands

### View logs
```bash
docker compose logs -f web
```

### Run Django shell
```bash
docker exec -it ecommerce_web python manage.py shell
```

### Run migrations
```bash
docker exec ecommerce_web python manage.py makemigrations
docker exec ecommerce_web python manage.py migrate
```

### Create superuser
```bash
docker exec -it ecommerce_web python manage.py createsuperuser
```

### Stop containers
```bash
docker compose down
```

### Reset database (WARNING: deletes all data)
```bash
docker compose down -v
docker compose up -d
docker exec ecommerce_web python manage.py migrate
```

## Admin Panel

Access the Django admin at: http://localhost:8000/admin/

Login with your superuser credentials.

## Multi-Tenant Architecture

- Each user belongs to a **Company**
- Users can only access data from their own company
- Products, orders, and other resources are automatically scoped by company
- `created_by` and `company` fields are set automatically from the authenticated user

## Security Notes

### For Production Deployment:

1. **Change SECRET_KEY**:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Update `.env` with the generated key.

2. **Set DEBUG=False** in `.env`

3. **Update ALLOWED_HOSTS** to your domain(s)

4. **Use strong DB password** and update `.env`

5. **Use HTTPS** with a reverse proxy (nginx/traefik)

6. **Set up proper CORS** origins in settings

## Testing

Access the interactive API documentation to test endpoints, or use curl/Postman:

**Example: Create a product**
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sample Product",
    "price": 99.99,
    "stock": 100,
    "is_active": true
  }'
```

**Example: Create an order**
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "orders": [
      {"product_id": 1, "quantity": 2}
    ]
  }'
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs web
docker compose logs db

# Restart services
docker compose restart
```

### Database connection errors
```bash
# Verify DB is healthy
docker compose ps

# Check credentials in .env match docker-compose.yml
cat .env
```

### Port already in use
```bash
# Stop other services using port 8000 or 3306
# Or change ports in docker-compose.yml
```

### Static files not loading
```bash
docker exec ecommerce_web python manage.py collectstatic --noinput
```

## License

This project is private and proprietary.

## Support

For issues or questions, contact the development team.
