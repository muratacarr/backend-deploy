# FastAPI Authentication System

## 🔐 Güvenli Kimlik Doğrulama ve Yetkilendirme Sistemi

Bu proje, JWT tabanlı kimlik doğrulama, OTP doğrulama, rol tabanlı yetkilendirme ve audit logging içeren kapsamlı bir FastAPI backend sistemidir.

## ✨ Özellikler

### 🔐 Kimlik Doğrulama

- **JWT Token** tabanlı authentication
- **OTP (One-Time Password)** doğrulama sistemi
- **Email** ile OTP gönderimi
- **Refresh Token** mekanizması
- **2FA (Two-Factor Authentication)** her login'de
- **Session management** ve güvenli logout
- **Token Blacklist Sistemi** - Logout sonrası token'ların geçersiz hale getirilmesi
- **JTI (JWT ID)** ile token takibi ve blacklist kontrolü

### 👥 Kullanıcı Yönetimi

- **Rol tabanlı yetkilendirme** (User, Moderator, Admin)
- **Permission sistemi** ile granüler erişim kontrolü
- **Kullanıcı kayıt** ve **hesap doğrulama**
- **Profil yönetimi** ve **şifre değiştirme**
- **Kullanıcı aktivasyon/deaktivasyon**
- **Soft delete** mekanizması

### 🛡️ Güvenlik

- **Audit logging** tüm kritik işlemler için
- **IP adresi** ve **user agent** takibi
- **Rate limiting** ve **input validation**
- **SQL injection** koruması
- **XSS** koruması
- **CORS** yapılandırması
- **HTTPS** desteği

### 📊 Yönetim Paneli

- **Admin dashboard** tam kullanıcı yönetimi
- **Moderator panel** sınırlı yönetici yetkileri
- **Audit log** görüntüleme ve analiz
- **Rol ve permission** yönetimi
- **Content moderation** sistemi
- **Report management** sistemi

### 📝 İçerik Yönetimi

- **Content CRUD** işlemleri
- **Content moderation** sistemi
- **Public/Private** içerik desteği
- **Author-based** içerik kontrolü

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Python 3.8+
- PostgreSQL (veya SQLite)
- SMTP sunucusu (email gönderimi için)
- Redis (opsiyonel, cache için)

### Kurulum

1. **Repository'yi klonlayın**

```bash
git clone <repository-url>
cd backend-deploy
```

2. **Virtual environment oluşturun**

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

3. **Bağımlılıkları yükleyin**

```bash
pip install -r requirements.txt
```

4. **Environment variables ayarlayın**

```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

5. **Veritabanını başlatın**

```bash
# PostgreSQL için
createdb your_database_name

# Migration'ları çalıştırın
alembic upgrade head
```

6. **Sunucuyu başlatın**

```bash
make run
# veya
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 API Endpoints ve Rol Erişim Matrisi

### 🔐 Authentication (`/api/v1/auth/`)

| Method | Endpoint          | Açıklama                   | User | Moderator | Admin | Permission |
| ------ | ----------------- | -------------------------- | ---- | --------- | ----- | ---------- |
| POST   | `/register`       | Kullanıcı kaydı            | ✅   | ✅        | ✅    | -          |
| POST   | `/login`          | Giriş yapma (OTP gönderir) | ✅   | ✅        | ✅    | -          |
| POST   | `/verify-login`   | OTP ile giriş doğrulama    | ✅   | ✅        | ✅    | -          |
| POST   | `/verify-account` | Hesap doğrulama            | ✅   | ✅        | ✅    | -          |
| POST   | `/resend-otp`     | OTP tekrar gönderme        | ✅   | ✅        | ✅    | -          |
| POST   | `/refresh`        | Token yenileme             | ✅   | ✅        | ✅    | -          |
| POST   | `/logout`         | Çıkış yapma                | ✅   | ✅        | ✅    | -          |
| GET    | `/me`             | Kendi profil bilgileri     | ✅   | ✅        | ✅    | -          |

### 👤 User Management (`/api/v1/users/`)

| Method | Endpoint                | Açıklama                    | User  | Moderator | Admin | Permission        |
| ------ | ----------------------- | --------------------------- | ----- | --------- | ----- | ----------------- |
| GET    | `/`                     | Tüm kullanıcıları listeleme | ❌    | ❌        | ✅    | `user_manage`     |
| GET    | `/{user_id}`            | Kullanıcı detayları         | Kendi | Kendi     | ✅    | `user_read`       |
| PUT    | `/{user_id}`            | Kullanıcı güncelleme        | Kendi | Kendi     | ✅    | `user_update_own` |
| PATCH  | `/{user_id}/role`       | Kullanıcı rolü güncelleme   | ❌    | ❌        | ✅    | `user_manage`     |
| DELETE | `/{user_id}`            | Kullanıcı silme             | ❌    | ❌        | ✅    | `user_manage`     |
| POST   | `/{user_id}/activate`   | Kullanıcı aktivasyonu       | ❌    | ❌        | ✅    | `user_manage`     |
| POST   | `/{user_id}/deactivate` | Kullanıcı deaktivasyonu     | ❌    | ❌        | ✅    | `user_manage`     |

### 🛡️ Admin Panel (`/api/v1/admin/`)

| Method | Endpoint           | Açıklama                     | User | Moderator | Admin | Permission    |
| ------ | ------------------ | ---------------------------- | ---- | --------- | ----- | ------------- |
| GET    | `/users`           | Tüm kullanıcıları yönetme    | ❌   | ❌        | ✅    | `user_manage` |
| GET    | `/users/{user_id}` | Kullanıcı detayları (admin)  | ❌   | ❌        | ✅    | `user_manage` |
| PUT    | `/users/{user_id}` | Kullanıcı güncelleme (admin) | ❌   | ❌        | ✅    | `user_manage` |
| DELETE | `/users/{user_id}` | Kullanıcı silme (admin)      | ❌   | ❌        | ✅    | `user_manage` |
| GET    | `/audit-logs`      | Audit logları görüntüleme    | ❌   | ❌        | ✅    | `audit_view`  |

### 🛠️ Moderator Panel (`/api/v1/moderator/`)

| Method | Endpoint                    | Açıklama                            | User | Moderator | Admin | Permission      |
| ------ | --------------------------- | ----------------------------------- | ---- | --------- | ----- | --------------- |
| GET    | `/users`                    | Moderation için kullanıcı listesi   | ❌   | ✅        | ✅    | `user_moderate` |
| GET    | `/users/{user_id}`          | Moderation için kullanıcı detayları | ❌   | ✅        | ✅    | `user_moderate` |
| PUT    | `/users/{user_id}/suspend`  | Kullanıcı askıya alma               | ❌   | ✅        | ✅    | `user_moderate` |
| PUT    | `/users/{user_id}/activate` | Kullanıcı aktivasyonu               | ❌   | ✅        | ✅    | `user_moderate` |
| GET    | `/reports`                  | Rapor yönetimi                      | ❌   | ✅        | ✅    | `report_manage` |

### 📝 Content Management (`/api/v1/content/`)

| Method | Endpoint                 | Açıklama           | User  | Moderator | Admin | Permission           |
| ------ | ------------------------ | ------------------ | ----- | --------- | ----- | -------------------- |
| POST   | `/`                      | İçerik oluşturma   | ✅    | ✅        | ✅    | `content_create`     |
| GET    | `/`                      | İçerik listeleme   | ✅    | ✅        | ✅    | `content_read`       |
| GET    | `/{content_id}`          | İçerik detayları   | ✅    | ✅        | ✅    | `content_read`       |
| PUT    | `/{content_id}`          | İçerik güncelleme  | Kendi | Kendi     | ✅    | `content_update_own` |
| DELETE | `/{content_id}`          | İçerik silme       | Kendi | Kendi     | ✅    | `content_delete_own` |
| PUT    | `/{content_id}/moderate` | İçerik moderasyonu | ❌    | ✅        | ✅    | `content_moderate`   |

### 🔑 Role Management (`/api/v1/roles/`)

| Method | Endpoint      | Açıklama                     | User | Moderator | Admin | Permission    |
| ------ | ------------- | ---------------------------- | ---- | --------- | ----- | ------------- |
| GET    | `/`           | Rolleri listeleme            | ❌   | ❌        | ✅    | `role_manage` |
| GET    | `/{role_id}`  | Rol detayları                | ❌   | ❌        | ✅    | `role_manage` |
| POST   | `/`           | Rol oluşturma                | ❌   | ❌        | ✅    | `role_manage` |
| PUT    | `/{role_id}`  | Rol güncelleme               | ❌   | ❌        | ✅    | `role_manage` |
| DELETE | `/{role_id}`  | Rol silme                    | ❌   | ❌        | ✅    | `role_manage` |
| POST   | `/initialize` | Varsayılan rolleri oluşturma | ❌   | ❌        | ✅    | `role_manage` |

### 📊 Audit Logs (`/api/v1/audit-logs/`)

| Method | Endpoint    | Açıklama                | User | Moderator | Admin | Permission   |
| ------ | ----------- | ----------------------- | ---- | --------- | ----- | ------------ |
| GET    | `/`         | Audit logları listeleme | ❌   | ❌        | ✅    | `audit_view` |
| GET    | `/{log_id}` | Audit log detayları     | ❌   | ❌        | ✅    | `audit_view` |

## 👥 Kullanıcı Rolleri ve Yetkileri

### 🔴 **User (Normal Kullanıcı) - Rol ID: 3**

**Temel Yetkiler:**

- Kendi profilini yönetme
- İçerik oluşturma ve yönetme
- Authentication işlemleri

**Permission'lar:**

- `user_read` - Kendi profilini okuma
- `user_update_own` - Kendi profilini güncelleme
- `content_read` - İçerik okuma
- `content_create` - İçerik oluşturma
- `content_update_own` - Kendi içeriğini güncelleme
- `content_delete_own` - Kendi içeriğini silme

**Erişebileceği Endpoint'ler:**

- ✅ `/api/v1/auth/*` - Tüm authentication endpoint'leri
- ✅ `/api/v1/users/{kendi_id}` - Kendi profilini görme/güncelleme
- ✅ `/api/v1/content/*` - İçerik CRUD işlemleri (kendi içeriği)

**Erişemeyeceği Endpoint'ler:**

- ❌ `/api/v1/users/` - Tüm kullanıcıları listeleme
- ❌ `/api/v1/admin/*` - Admin paneli
- ❌ `/api/v1/moderator/*` - Moderator paneli
- ❌ `/api/v1/roles/*` - Rol yönetimi
- ❌ `/api/v1/audit-logs/*` - Audit logları

---

### 🟡 **Moderator (Moderatör) - Rol ID: 2**

**Temel Yetkiler:**

- User yetkileri + moderasyon yetkileri
- Kullanıcı moderasyonu
- İçerik moderasyonu
- Rapor yönetimi

**Permission'lar:**

- **User permissions** (yukarıdaki tümü) +
- `content_moderate` - İçerik moderasyonu
- `user_moderate` - Kullanıcı moderasyonu
- `report_manage` - Rapor yönetimi

**Erişebileceği Endpoint'ler:**

- ✅ Tüm User endpoint'leri
- ✅ `/api/v1/moderator/users` - Moderation için kullanıcı listesi
- ✅ `/api/v1/moderator/users/{user_id}` - Kullanıcı detayları (moderation)
- ✅ `/api/v1/moderator/users/{user_id}/suspend` - Kullanıcı askıya alma
- ✅ `/api/v1/moderator/users/{user_id}/activate` - Kullanıcı aktivasyonu
- ✅ `/api/v1/moderator/reports` - Rapor yönetimi
- ✅ `/api/v1/content/{content_id}/moderate` - İçerik moderasyonu

**Erişemeyeceği Endpoint'ler:**

- ❌ `/api/v1/admin/*` - Admin paneli
- ❌ `/api/v1/roles/*` - Rol yönetimi
- ❌ `/api/v1/audit-logs/*` - Audit logları

---

### 🟢 **Admin (Yönetici) - Rol ID: 1**

**Temel Yetkiler:**

- Tüm yetkiler
- Tam sistem yönetimi
- Kullanıcı, rol ve permission yönetimi
- Audit logları görüntüleme

**Permission'lar:**

- **Moderator permissions** (yukarıdaki tümü) +
- `user_manage` - Kullanıcı yönetimi
- `role_manage` - Rol yönetimi
- `system_manage` - Sistem yönetimi
- `audit_view` - Audit logları görme

**Erişebileceği Endpoint'ler:**

- ✅ Tüm User ve Moderator endpoint'leri
- ✅ `/api/v1/admin/users` - Tüm kullanıcıları yönetme
- ✅ `/api/v1/admin/users/{user_id}` - Kullanıcı detayları (admin)
- ✅ `/api/v1/admin/users/{user_id}` (PUT) - Kullanıcı güncelleme (admin)
- ✅ `/api/v1/admin/users/{user_id}` (DELETE) - Kullanıcı silme (admin)
- ✅ `/api/v1/admin/audit-logs` - Audit logları görüntüleme
- ✅ `/api/v1/roles/*` - Rol yönetimi
- ✅ `/api/v1/audit-logs/*` - Audit logları

**Özel Admin Yetkileri:**

- Kullanıcı silme
- Rol değiştirme
- Sistem yönetimi
- Audit logları görüntüleme

## 🔐 Permission Sistemi Detayları

### **Permission Kategorileri:**

#### 👤 **User Permissions (Kullanıcı Yetkileri)**

- `user_read` - Kendi profilini okuma
- `user_update_own` - Kendi profilini güncelleme

#### 📝 **Content Permissions (İçerik Yetkileri)**

- `content_read` - İçerik okuma
- `content_create` - İçerik oluşturma
- `content_update_own` - Kendi içeriğini güncelleme
- `content_delete_own` - Kendi içeriğini silme
- `content_moderate` - İçerik moderasyonu

#### 🛠️ **Moderation Permissions (Moderasyon Yetkileri)**

- `user_moderate` - Kullanıcı moderasyonu
- `report_manage` - Rapor yönetimi

#### 🛡️ **Admin Permissions (Yönetici Yetkileri)**

- `user_manage` - Kullanıcı yönetimi
- `role_manage` - Rol yönetimi
- `system_manage` - Sistem yönetimi
- `audit_view` - Audit logları görme

### **Permission Hiyerarşisi:**

```
Admin (Tüm yetkiler)
├── Moderator Permissions
│   ├── User Permissions
│   ├── Content Permissions
│   └── Moderation Permissions
└── Admin Permissions

Moderator (Sınırlı yönetici yetkileri)
├── User Permissions
├── Content Permissions
└── Moderation Permissions

User (Temel kullanıcı yetkileri)
├── User Permissions
└── Content Permissions
```

## 📱 Kullanım Örnekleri

### 🔐 **Login Akışı**

1. **Login (OTP gönderir)**

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

2. **OTP Doğrula (Token alır)**

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

### 👤 **User İşlemleri**

```bash
# Kendi profilini görme
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/users/123"

# İçerik oluşturma
curl -X POST "http://localhost:8000/api/v1/content/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Content",
    "content": "This is my content",
    "is_public": true
  }'
```

### 🛡️ **Admin İşlemleri**

```bash
# Tüm kullanıcıları listeleme
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/admin/users"

# Kullanıcı silme
curl -X DELETE "http://localhost:8000/api/v1/admin/users/123" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Audit logları görme
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/admin/audit-logs"
```

### 🛠️ **Moderator İşlemleri**

```bash
# Kullanıcıları moderasyon için listeleme
curl -H "Authorization: Bearer MODERATOR_TOKEN" \
  "http://localhost:8000/api/v1/moderator/users"

# Kullanıcıyı askıya alma
curl -X PUT "http://localhost:8000/api/v1/moderator/users/123/suspend" \
  -H "Authorization: Bearer MODERATOR_TOKEN"

# İçerik moderasyonu
curl -X PUT "http://localhost:8000/api/v1/content/456/moderate" \
  -H "Authorization: Bearer MODERATOR_TOKEN"
```

## 🛠️ Geliştirme

### Makefile Komutları

```bash
# Sunucuyu başlat (port kontrolü ile)
make run

# Sadece portu boşalt
make kill-port

# Sunucuyu durdur
make stop
```

### Veritabanı İşlemleri

```bash
# Migration oluştur
alembic revision --autogenerate -m "Description"

# Migration uygula
alembic upgrade head

# Migration geri al
alembic downgrade -1
```

### Test

```bash
# Testleri çalıştır
python -m pytest tests/ -v

# Coverage raporu
python -m pytest tests/ --cov=app --cov-report=html
```

## 🔧 Konfigürasyon

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

## 📊 Monitoring ve Logging

### Audit Logs

- Tüm kritik işlemler loglanır
- IP adresi ve user agent kaydedilir
- Başarılı/başarısız işlemler ayrı ayrı loglanır
- Log seviyeleri: DEBUG, INFO, WARNING, ERROR

### Log Dosyaları

- `logs/app.log` - Genel uygulama logları
- `logs/error.log` - Hata logları

### Log Formatı

```
2025-10-05 17:20:58 | INFO | app.services.auth_service:login_success:45 - User 123 logged in successfully
```

## 🚀 Production Deployment

### Docker ile Deploy

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

## 🔒 Güvenlik Best Practices

### JWT Token Güvenliği

- Token'lar kısa süreli (30 dakika)
- Refresh token'lar uzun süreli (7 gün)
- Token'lar HTTPS üzerinden gönderilmeli
- **Token Blacklist Sistemi**: Logout'ta token'lar blacklist'e eklenir ve geçersiz hale getirilir
- **JTI (JWT ID)**: Her token'ın benzersiz kimliği ile blacklist kontrolü
- **Otomatik Blacklist Kontrolü**: Her API isteğinde token blacklist kontrolü yapılır
- **Güvenli Logout**: Logout sonrası eski token ile hiçbir işlem yapılamaz

### OTP Güvenliği

- OTP'ler 5 dakika geçerli
- OTP'ler sadece bir kez kullanılabilir
- OTP'ler email ile gönderilir
- OTP'ler log'da görünmez (production'da)

### Database Güvenliği

- SQL injection koruması
- Prepared statements kullanımı
- Connection pooling
- Database backup'ları

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 📞 İletişim

- **Proje Sahibi**: [Your Name]
- **Email**: your.email@example.com
- **GitHub**: [Your GitHub Profile]

## 🙏 Teşekkürler

- FastAPI ekibine
- SQLAlchemy ekibine
- Tüm açık kaynak katkıda bulunanlara

---

**Not**: Bu sistem production ortamında kullanılmadan önce güvenlik testlerinden geçirilmelidir.

## 📚 Ek Kaynaklar

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc7519)
- [OWASP Security Guidelines](https://owasp.org/)
