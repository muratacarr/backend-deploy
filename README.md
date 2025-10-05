# FastAPI Authentication System

## 🔐 Secure Authentication and Authorization System

This project is a comprehensive FastAPI backend system that includes JWT-based authentication, OTP verification, role-based authorization, and audit logging.

## ✨ Features

### 🔐 Authentication

- **JWT Token** based authentication
- **OTP (One-Time Password)** verification system
- **Email** OTP delivery
- **Refresh Token** mechanism
- **2FA (Two-Factor Authentication)** on every login
- **Session management** and secure logout
- **Token Blacklist System** - Tokens are invalidated after logout
- **JTI (JWT ID)** for token tracking and blacklist control

### 👥 User Management

- **Role-based authorization** (User, Moderator, Admin)
- **Permission system** with granular access control
- **User registration** and **account verification**
- **Profile management** and **password change**
- **User activation/deactivation**
- **Soft delete** mechanism

### 🛡️ Security

- **Audit logging** for all critical operations
- **IP address** and **user agent** tracking
- **Rate limiting** and **input validation**
- **SQL injection** protection
- **XSS** protection
- **CORS** configuration
- **HTTPS** support

### 📊 Admin Panel

- **Admin dashboard** for complete user management
- **Moderator panel** with limited admin privileges
- **Audit log** viewing and analysis
- **Role and permission** management
- **Content moderation** system
- **Report management** system

### 📝 Content Management

- **Content CRUD** operations
- **Content moderation** system
- **Public/Private** content support
- **Author-based** content control

## 🚀 Quick Start

### Requirements

- Python 3.8+
- PostgreSQL (or SQLite)
- SMTP server (for email sending)
- Redis (optional, for caching)

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd backend-deploy
```

2. **Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set environment variables**

```bash
cp .env.example .env
# Edit the .env file
```

5. **Initialize database**

```bash
# For PostgreSQL
createdb your_database_name

# Run migrations
alembic upgrade head
```

6. **Start the server**

```bash
make run
# or
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 API Endpoints and Role Access Matrix

### 🔐 Authentication (`/api/v1/auth/`)

| Method | Endpoint          | Description             | User | Moderator | Admin | Permission |
| ------ | ----------------- | ----------------------- | ---- | --------- | ----- | ---------- |
| POST   | `/register`       | User registration       | ✅   | ✅        | ✅    | -          |
| POST   | `/login`          | Login (sends OTP)       | ✅   | ✅        | ✅    | -          |
| POST   | `/verify-login`   | OTP login verification  | ✅   | ✅        | ✅    | -          |
| POST   | `/verify-account` | Account verification    | ✅   | ✅        | ✅    | -          |
| POST   | `/resend-otp`     | Resend OTP              | ✅   | ✅        | ✅    | -          |
| POST   | `/refresh`        | Token refresh           | ✅   | ✅        | ✅    | -          |
| POST   | `/logout`         | Logout                  | ✅   | ✅        | ✅    | -          |
| GET    | `/me`             | Own profile information | ✅   | ✅        | ✅    | -          |

### 👤 User Management (`/api/v1/users/`)

| Method | Endpoint                | Description      | User | Moderator | Admin | Permission        |
| ------ | ----------------------- | ---------------- | ---- | --------- | ----- | ----------------- |
| GET    | `/`                     | List all users   | ❌   | ❌        | ✅    | `user_manage`     |
| GET    | `/{user_id}`            | User details     | Own  | Own       | ✅    | `user_read`       |
| PUT    | `/{user_id}`            | Update user      | Own  | Own       | ✅    | `user_update_own` |
| PATCH  | `/{user_id}/role`       | Update user role | ❌   | ❌        | ✅    | `user_manage`     |
| DELETE | `/{user_id}`            | Delete user      | ❌   | ❌        | ✅    | `user_manage`     |
| POST   | `/{user_id}/activate`   | Activate user    | ❌   | ❌        | ✅    | `user_manage`     |
| POST   | `/{user_id}/deactivate` | Deactivate user  | ❌   | ❌        | ✅    | `user_manage`     |

### 🛡️ Admin Panel (`/api/v1/admin/`)

| Method | Endpoint           | Description          | User | Moderator | Admin | Permission    |
| ------ | ------------------ | -------------------- | ---- | --------- | ----- | ------------- |
| GET    | `/users`           | Manage all users     | ❌   | ❌        | ✅    | `user_manage` |
| GET    | `/users/{user_id}` | User details (admin) | ❌   | ❌        | ✅    | `user_manage` |
| PUT    | `/users/{user_id}` | Update user (admin)  | ❌   | ❌        | ✅    | `user_manage` |
| DELETE | `/users/{user_id}` | Delete user (admin)  | ❌   | ❌        | ✅    | `user_manage` |
| GET    | `/audit-logs`      | View audit logs      | ❌   | ❌        | ✅    | `audit_view`  |

### 🛠️ Moderator Panel (`/api/v1/moderator/`)

| Method | Endpoint                    | Description                 | User | Moderator | Admin | Permission      |
| ------ | --------------------------- | --------------------------- | ---- | --------- | ----- | --------------- |
| GET    | `/users`                    | User list for moderation    | ❌   | ✅        | ✅    | `user_moderate` |
| GET    | `/users/{user_id}`          | User details for moderation | ❌   | ✅        | ✅    | `user_moderate` |
| PUT    | `/users/{user_id}/suspend`  | Suspend user                | ❌   | ✅        | ✅    | `user_moderate` |
| PUT    | `/users/{user_id}/activate` | Activate user               | ❌   | ✅        | ✅    | `user_moderate` |
| GET    | `/reports`                  | Report management           | ❌   | ✅        | ✅    | `report_manage` |

### 📝 Content Management (`/api/v1/content/`)

| Method | Endpoint                 | Description        | User | Moderator | Admin | Permission           |
| ------ | ------------------------ | ------------------ | ---- | --------- | ----- | -------------------- |
| POST   | `/`                      | Create content     | ✅   | ✅        | ✅    | `content_create`     |
| GET    | `/`                      | List content       | ✅   | ✅        | ✅    | `content_read`       |
| GET    | `/{content_id}`          | Content details    | ✅   | ✅        | ✅    | `content_read`       |
| PUT    | `/{content_id}`          | Update content     | Own  | Own       | ✅    | `content_update_own` |
| DELETE | `/{content_id}`          | Delete content     | Own  | Own       | ✅    | `content_delete_own` |
| PUT    | `/{content_id}/moderate` | Content moderation | ❌   | ✅        | ✅    | `content_moderate`   |

### 🔑 Role Management (`/api/v1/roles/`)

| Method | Endpoint      | Description          | User | Moderator | Admin | Permission    |
| ------ | ------------- | -------------------- | ---- | --------- | ----- | ------------- |
| GET    | `/`           | List roles           | ❌   | ❌        | ✅    | `role_manage` |
| GET    | `/{role_id}`  | Role details         | ❌   | ❌        | ✅    | `role_manage` |
| POST   | `/`           | Create role          | ❌   | ❌        | ✅    | `role_manage` |
| PUT    | `/{role_id}`  | Update role          | ❌   | ❌        | ✅    | `role_manage` |
| DELETE | `/{role_id}`  | Delete role          | ❌   | ❌        | ✅    | `role_manage` |
| POST   | `/initialize` | Create default roles | ❌   | ❌        | ✅    | `role_manage` |

### 📊 Audit Logs (`/api/v1/audit-logs/`)

| Method | Endpoint    | Description       | User | Moderator | Admin | Permission   |
| ------ | ----------- | ----------------- | ---- | --------- | ----- | ------------ |
| GET    | `/`         | List audit logs   | ❌   | ❌        | ✅    | `audit_view` |
| GET    | `/{log_id}` | Audit log details | ❌   | ❌        | ✅    | `audit_view` |

## 👥 User Roles and Permissions

### 🔴 **User (Normal User) - Role ID: 3**

**Basic Permissions:**

- Manage own profile
- Create and manage content
- Authentication operations

**Permissions:**

- `user_read` - Read own profile
- `user_update_own` - Update own profile
- `content_read` - Read content
- `content_create` - Create content
- `content_update_own` - Update own content
- `content_delete_own` - Delete own content

**Accessible Endpoints:**

- ✅ `/api/v1/auth/*` - All authentication endpoints
- ✅ `/api/v1/users/{own_id}` - View/update own profile
- ✅ `/api/v1/content/*` - Content CRUD operations (own content)

**Restricted Endpoints:**

- ❌ `/api/v1/users/` - List all users
- ❌ `/api/v1/admin/*` - Admin panel
- ❌ `/api/v1/moderator/*` - Moderator panel
- ❌ `/api/v1/roles/*` - Role management
- ❌ `/api/v1/audit-logs/*` - Audit logs

---

### 🟡 **Moderator (Moderator) - Role ID: 2**

**Basic Permissions:**

- User permissions + moderation permissions
- User moderation
- Content moderation
- Report management

**Permissions:**

- **User permissions** (all above) +
- `content_moderate` - Content moderation
- `user_moderate` - User moderation
- `report_manage` - Report management

**Accessible Endpoints:**

- ✅ All User endpoints
- ✅ `/api/v1/moderator/users` - User list for moderation
- ✅ `/api/v1/moderator/users/{user_id}` - User details (moderation)
- ✅ `/api/v1/moderator/users/{user_id}/suspend` - Suspend user
- ✅ `/api/v1/moderator/users/{user_id}/activate` - Activate user
- ✅ `/api/v1/moderator/reports` - Report management
- ✅ `/api/v1/content/{content_id}/moderate` - Content moderation

**Restricted Endpoints:**

- ❌ `/api/v1/admin/*` - Admin panel
- ❌ `/api/v1/roles/*` - Role management
- ❌ `/api/v1/audit-logs/*` - Audit logs

---

### 🟢 **Admin (Administrator) - Role ID: 1**

**Basic Permissions:**

- All permissions
- Complete system management
- User, role and permission management
- Audit log viewing

**Permissions:**

- **Moderator permissions** (all above) +
- `user_manage` - User management
- `role_manage` - Role management
- `system_manage` - System management
- `audit_view` - View audit logs

**Accessible Endpoints:**

- ✅ All User and Moderator endpoints
- ✅ `/api/v1/admin/users` - Manage all users
- ✅ `/api/v1/admin/users/{user_id}` - User details (admin)
- ✅ `/api/v1/admin/users/{user_id}` (PUT) - Update user (admin)
- ✅ `/api/v1/admin/users/{user_id}` (DELETE) - Delete user (admin)
- ✅ `/api/v1/admin/audit-logs` - View audit logs
- ✅ `/api/v1/roles/*` - Role management
- ✅ `/api/v1/audit-logs/*` - Audit logs

**Special Admin Permissions:**

- Delete users
- Change roles
- System management
- View audit logs

## 🔐 Permission System Details

### **Permission Categories:**

#### 👤 **User Permissions (User Rights)**

- `user_read` - Read own profile
- `user_update_own` - Update own profile

#### 📝 **Content Permissions (Content Rights)**

- `content_read` - Read content
- `content_create` - Create content
- `content_update_own` - Update own content
- `content_delete_own` - Delete own content
- `content_moderate` - Content moderation

#### 🛠️ **Moderation Permissions (Moderation Rights)**

- `user_moderate` - User moderation
- `report_manage` - Report management

#### 🛡️ **Admin Permissions (Administrator Rights)**

- `user_manage` - User management
- `role_manage` - Role management
- `system_manage` - System management
- `audit_view` - View audit logs

### **Permission Hierarchy:**

```
Admin (All permissions)
├── Moderator Permissions
│   ├── User Permissions
│   ├── Content Permissions
│   └── Moderation Permissions
└── Admin Permissions

Moderator (Limited admin privileges)
├── User Permissions
├── Content Permissions
└── Moderation Permissions

User (Basic user permissions)
├── User Permissions
└── Content Permissions
```

## 📱 Usage Examples

### 🔐 **Login Flow**

1. **Login (sends OTP)**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Response:
{
  "message": "OTP sent to your email. Please verify to complete login.",
  "email": "user@example.com",
  "requires_otp_verification": true,
  "expires_in_minutes": 5
}
```

2. **Verify OTP (get token)**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/verify-login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp_code": "123456"
  }'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 👤 **User Operations**

```bash
# View own profile
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/users/123"

# Create content
curl -X POST "http://localhost:8000/api/v1/content/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Content",
    "content": "This is my content",
    "is_public": true
  }'
```

### 🛡️ **Admin Operations**

```bash
# List all users
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/admin/users"

# Delete user
curl -X DELETE "http://localhost:8000/api/v1/admin/users/123" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# View audit logs
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/admin/audit-logs"
```

### 🛠️ **Moderator Operations**

```bash
# List users for moderation
curl -H "Authorization: Bearer MODERATOR_TOKEN" \
  "http://localhost:8000/api/v1/moderator/users"

# Suspend user
curl -X PUT "http://localhost:8000/api/v1/moderator/users/123/suspend" \
  -H "Authorization: Bearer MODERATOR_TOKEN"

# Moderate content
curl -X PUT "http://localhost:8000/api/v1/content/456/moderate" \
  -H "Authorization: Bearer MODERATOR_TOKEN"
```

## 🛠️ Development

### Makefile Commands

```bash
# Start server (with port check)
make run

# Just free the port
make kill-port

# Stop server
make stop
```

### Database Operations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing

```bash
# Run tests
python -m pytest tests/ -v

# Coverage report
python -m pytest tests/ --cov=app --cov-report=html
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# App
APP_NAME=FastAPI Auth System
DEBUG=True
```

## 📊 Monitoring and Logging

### Audit Logs

- All critical operations are logged
- IP address and user agent are recorded
- Successful/failed operations are logged separately
- Log levels: DEBUG, INFO, WARNING, ERROR

### Log Files

- `logs/app.log` - General application logs
- `logs/error.log` - Error logs

### Log Format

```
2025-10-05 17:20:58 | INFO | app.services.auth_service:login_success:45 - User 123 logged in successfully
```

## 🚀 Production Deployment

### Deploy with Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dbname
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: dbname
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Environment Setup

```bash
# Production environment variables
export DATABASE_URL="postgresql://user:pass@host:5432/db"
export SECRET_KEY="production-secret-key"
export DEBUG=False
export SMTP_HOST="smtp.gmail.com"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
```

## 🔒 Security Best Practices

### JWT Token Security

- Tokens are short-lived (30 minutes)
- Refresh tokens are long-lived (7 days)
- Tokens should be sent over HTTPS
- **Token Blacklist System**: Tokens are added to blacklist on logout and invalidated
- **JTI (JWT ID)**: Unique token identity for blacklist control
- **Automatic Blacklist Check**: Token blacklist check on every API request
- **Secure Logout**: No operations can be performed with old tokens after logout

### OTP Security

- OTPs are valid for 5 minutes
- OTPs can only be used once
- OTPs are sent via email
- OTPs are not visible in logs (in production)

### Database Security

- SQL injection protection
- Prepared statements usage
- Connection pooling
- Database backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 📞 Contact

- **Project Owner**: [Your Name]
- **Email**: your.email@example.com
- **GitHub**: [Your GitHub Profile]

## 🙏 Acknowledgments

- FastAPI team
- SQLAlchemy team
- All open source contributors

---

**Note**: This system should undergo security testing before being used in production

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc7519)
- [OWASP Security Guidelines](https://owasp.org/)
