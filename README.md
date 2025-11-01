# Django Backend API Documentation

---

## Overview

This project is a Django REST API that implements role-based access control (RBAC) for managing users, products, orders, and email-based invitations. Authentication is handled via JSON Web Tokens (JWT) using `djangorestframework-simplejwt` with token blacklisting enabled for logout.

- Base URL: `/api/`
- Auth endpoints: `/api/token`, `/api/token/refresh`, `/api/logout`
- API resources: `users`, `products`, `orders`, `invitations`
- Default permission: Authenticated requests only (unless otherwise noted)

---

## Getting Started

### Requirements
- Python 3.11+
- MySQL (or compatible)
- Django 5.2+
- Django REST Framework
- djangorestframework-simplejwt

### Environment Variables
Create a `.env` file in the project root (same level as `backend/settings.py`):

```
SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### Install and Run (local)

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8890
```

### Docker (optional)
A `docker-compose.yml` is provided. Example:

```
docker compose up -d --build
```

---

## Authentication

The API uses JWT bearer tokens.

- Obtain access and refresh tokens: `POST /api/token`
- Refresh access token: `POST /api/token/refresh`
- Logout (blacklist refresh token): `POST /api/logout`

Include the access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Obtain Token
- Endpoint: `POST /api/token`
- Body (JSON):
```
{
  "username": "admin",
  "password": "admin_password"
}
```
- Response 200:
```
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

### Refresh Token
- Endpoint: `POST /api/token/refresh`
- Body (JSON):
```
{ "refresh": "<refresh_token>" }
```
- Response 200:
```
{ "access": "<new_access_token>" }
```

### Logout
- Endpoint: `POST /api/logout`
- Body (JSON):
```
{ "refresh": "<refresh_token>" }
```
- Responses:
  - 205: `{ "detail": "Successfully logged out" }`
  - 400: `{ "detail": "Invalid or expired token" }` or `{ "detail": "Refresh token required" }`

---

## Role-Based Access Control (RBAC)

User roles:
- `admin`: full access to all resources
- `manager`: read-only for Users and Orders; full access for Products
- `staff`: read-only for Products; no access to Users and Orders

Permissions are enforced by custom permission classes:
- Users: `UserPermission`
- Products: `ProductPermission`
- Orders: `OrderPermission`
- Invitations: Requires authentication; creation limited to `admin` and `manager` via view logic

---

## Resources and Endpoints

Router base: `/api/`

### Users
- Base: `/api/users`
- Permissions: `admin` (full), `manager` (read-only), `staff` (no access)

Endpoints:
- `GET /api/users` — list users
- `POST /api/users` — create user
  - If requester is `admin`, the create serializer accepts password and role
- `GET /api/users/{id}` — retrieve user
- `PUT /api/users/{id}` — update user
- `PATCH /api/users/{id}` — partial update
- `DELETE /api/users/{id}` — delete user

Request/Response schema:
- Read serializer (`UserSerializer`):
```
{
  "id": 1,
  "username": "jane",
  "email": "jane@example.com",
  "role": "staff",
  "first_name": "Jane",
  "last_name": "Doe"
}
```
- Admin create serializer (`AdminCreateUserSerializer`):
```
{
  "username": "john",
  "email": "john@example.com",
  "role": "manager",
  "password": "StrongPass123!",
  "first_name": "John",
  "last_name": "Smith"
}
```

Notes:
- Non-admin create attempts will ignore `password` and `role` fields (uses `UserSerializer`).

---

### Products
- Base: `/api/products`
- Permissions: `admin` and `manager` (full), `staff` (read-only)

Endpoints:
- `GET /api/products` — list products
- `POST /api/products` — create product
- `GET /api/products/{id}` — retrieve product
- `PUT /api/products/{id}` — update product
- `PATCH /api/products/{id}` — partial update
- `DELETE /api/products/{id}` — delete product

Request (create/update):
```
{
  "name": "Keyboard",
  "price": 79.99,
  "stock": 50,
  "status": true
}
```

Response:
```
{
  "id": 10,
  "name": "Keyboard",
  "price": 79.99,
  "stock": 50,
  "status": true,
  "created_at": "2025-01-01T10:00:00Z"
}
```

---

### Orders
- Base: `/api/orders`
- Permissions: `admin` (full), `manager` (read-only), `staff` (no access)

Endpoints:
- `GET /api/orders` — list orders
- `POST /api/orders` — create order
- `GET /api/orders/{id}` — retrieve order
- `PUT /api/orders/{id}` — update order
- `PATCH /api/orders/{id}` — partial update
- `DELETE /api/orders/{id}` — delete order

Request (create):
```
{
  "product_id": 3,
  "customer_name": "Acme Inc.",
  "quantity": 2
}
```

Response:
```
{
  "id": 42,
  "product": {
    "id": 3,
    "name": "Keyboard",
    "price": 79.99
  },
  "customer_name": "Acme Inc.",
  "quantity": 2,
  "total_price": 159.98,
  "status": "Pending",
  "created_at": "2025-01-01T10:00:00Z"
}
```

Notes:
- `total_price` is computed on create based on `product.price * quantity` and is read-only.

---

### Invitations
- Base: `/api/invitations`
- Permissions: Authenticated. Creation limited to `admin` and `manager`.

Endpoints:
- `GET /api/invitations` — list invitations (authenticated users)
- `POST /api/invitations` — create invitation (only `admin` and `manager`)
- `GET /api/invitations/{id}` — retrieve invitation
- `POST /api/invitations/accept` — accept invitation and create account (AllowAny)
  - Token can be provided in body or query string

Create invitation request:
```
{
  "email": "new.user@example.com",
  "role": "staff"
}
```

Create invitation response (201):
```
{
  "id": 7,
  "email": "new.user@example.com",
  "role": "staff",
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "inviter": 1,
  "is_used": false,
  "created_at": "2025-01-01T10:00:00Z",
  "expires_at": "2025-01-08T10:00:00Z"
}
```

Accept invitation request (body or query):
```
POST /api/invitations/accept
{
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "username": "newuser",
  "password": "StrongPass123!",
  "first_name": "New",
  "last_name": "User"
}
```

Accept invitation responses:
- 201: `{ "detail": "account created" }`
- 400: e.g. `{ "detail": "token required" }`, `{ "detail": "Invalid or expired token" }`, `{ "detail": "username exists" }`
- 403: `{ "detail": "Forbidden" }` when non-admin/manager tries to create an invitation

Notes:
- On creation, an email is sent with an acceptance link. In development, emails are printed to console via `EMAIL_BACKEND`.
- Invitation validity: valid if not used and not expired (7 days default).

---

## Error Handling

Common status codes:
- 200 OK — Successful read
- 201 Created — Successful write/creation
- 204 No Content — Successful deletion
- 400 Bad Request — Validation errors, missing parameters
- 401 Unauthorized — Missing/invalid JWT
- 403 Forbidden — Insufficient permissions by role
- 404 Not Found — Resource not found

Typical error shape:
```
{ "detail": "error message" }
```

---

## Development Notes

- Trailing slashes are disabled globally (`APPEND_SLASH=False`). Endpoints are defined without trailing slashes.
- Default permissions require authentication; endpoints explicitly allowing anonymous access are noted (e.g., `POST /api/invitations/accept`).
- Custom user model is `adminapi.User` with roles: `admin`, `manager`, `staff`.
- `Logout` requires the refresh token to blacklist it. Access tokens remain valid until expiry.

---

## Examples with curl

```
# Login
curl -s -X POST http://localhost:8890/api/token \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin_password"}'

# List products
curl -s http://localhost:8890/api/products \
  -H 'Authorization: Bearer <access_token>'

# Create product
curl -s -X POST http://localhost:8890/api/products \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"name":"Keyboard","price":79.99,"stock":50,"status":true}'

# Create invitation (admin/manager only)
curl -s -X POST http://localhost:8890/api/invitations \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"email":"new.user@example.com","role":"staff"}'

# Accept invitation
curl -s -X POST http://localhost:8890/api/invitations/accept \
  -H 'Content-Type: application/json' \
  -d '{"token":"<token>","username":"newuser","password":"StrongPass123!"}'

# Logout
curl -s -X POST http://localhost:8890/api/logout \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"refresh":"<refresh_token>"}'
```

---

## OpenAPI / Swagger

```
  - http://localhost:8890/api/docs/redoc
  - http://localhost:8890/api/docs/swagger
```
---

## License

MIT (or project-specific)
