# AI Helpdesk – Các lệnh vận hành và kiểm tra môi trường

Tài liệu nhanh cho quá trình phát triển dự án **AI Helpdesk** trên Windows + PowerShell.

> Thư mục backend hiện tại:
>
> `E:\Git_New\GITHUB\ai-helpdesk\backend`
>
> PostgreSQL chạy bằng Docker container:
>
> `ai-helpdesk-postgres`
>
> Database:
>
> `ai_helpdesk`
>
> User:
>
> `ai_helpdesk`

---

## 1. Vào thư mục Backend

```powershell
cd E:\Git_New\GITHUB\ai-helpdesk\backend
```

Kiểm tra thư mục hiện tại:

```powershell
Get-Location
```

---

## 2. Kích hoạt Python Virtual Environment

### PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

Khi thành công sẽ thấy:

```text
(.venv) PS E:\Git_New\GITHUB\ai-helpdesk\backend>
```

### Kiểm tra Python đang sử dụng

```powershell
python --version
```

```powershell
Get-Command python
```

Kết quả `python` phải trỏ vào:

```text
backend\.venv\Scripts\python.exe
```

### Kiểm tra pip

```powershell
python -m pip --version
```

### Thoát .venv

```powershell
deactivate
```

---

# 3. Chạy FastAPI

Từ thư mục `backend` và sau khi đã kích hoạt `.venv`:

```powershell
uvicorn app.main:app --reload
```

Server:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

Dừng server:

```text
CTRL + C
```

---

# 4. Kiểm tra FastAPI bằng PowerShell

## Health check

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Kết quả mong muốn:

```text
status
------
ok
```

## Database health check

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health/db
```

Kết quả phải cho biết:

```text
status   database
------   --------
ok       ai_helpdesk
```

---

# 5. Kiểm tra FastAPI Routes bằng Python

Liệt kê route:

```powershell
python -c "from app.main import app; [print(type(r).__name__, getattr(r, 'path', None)) for r in app.routes]"
```

Kiểm tra riêng Ticket API thông qua OpenAPI:

```powershell
python -c "from app.main import app; print([p for p in app.openapi()['paths'] if 'ticket' in p])"
```

Kết quả mong muốn:

```text
['/api/v1/tickets', '/api/v1/tickets/{ticket_id}']
```

---

# 6. Kiểm tra từng tầng của Ticket

## SQLAlchemy Models

```powershell
python -c "from app.models import Base; print(sorted(Base.metadata.tables.keys()))"
```

Kết quả hiện tại cần có 10 bảng:

```text
ai_conversations
ai_messages
audit_logs
knowledge_chunks
knowledge_documents
organizations
ticket_categories
ticket_comments
tickets
users
```

## Ticket Repository

```powershell
python -c "from app.repositories.ticket import TicketRepository; print('TicketRepository OK')"
```

## Ticket Schemas

```powershell
python -c "from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse; print('Ticket schemas OK')"
```

## Ticket Service

```powershell
python -c "from app.services.ticket import TicketService; print('TicketService OK')"
```

## Ticket Router

```powershell
python -c "from app.api.routes.tickets import router; print('Ticket Router OK')"
```

## DB Session

```powershell
python -c "from app.core.database import get_db; print('get_db OK')"
```

---

# 7. Alembic

Tất cả lệnh Alembic chạy tại:

```text
backend
```

và phải có `.venv` đang hoạt động.

## Kiểm tra Alembic

```powershell
alembic --version
```

## Kiểm tra Model và Migration có đồng bộ không

```powershell
alembic check
```

Nếu không có thay đổi cần migration, Alembic sẽ báo không có pending model changes.

## Xem lịch sử migration

```powershell
alembic history
```

## Xem migration hiện tại trong database

```powershell
alembic current
```

## Xem migration head

```powershell
alembic heads
```

## Tạo migration mới

```powershell
alembic revision --autogenerate -m "Describe change"
```

Ví dụ:

```powershell
alembic revision --autogenerate -m "Add ticket fields"
```

## Chạy migration

```powershell
alembic upgrade head
```

## Rollback 1 migration

```powershell
alembic downgrade -1
```

> Không chạy `downgrade` trên database production nếu chưa xác định rõ dữ liệu sẽ bị ảnh hưởng như thế nào.

---

# 8. Vào PostgreSQL bằng Docker

Container PostgreSQL:

```text
ai-helpdesk-postgres
```

Kết nối:

```powershell
docker exec -it ai-helpdesk-postgres psql -U ai_helpdesk -d ai_helpdesk
```

Không dùng:

```powershell
docker exec -it ai-helpdesk-postgres psql -U postgres -d ai_helpdesk
```

vì PostgreSQL hiện tại được tạo với user:

```text
ai_helpdesk
```

---

# 9. Các lệnh PostgreSQL thường dùng

Sau khi thấy:

```text
ai_helpdesk=#
```

## Liệt kê database

```sql
\l
```

## Liệt kê bảng

```sql
\dt
```

## Xem cấu trúc bảng

```sql
\d tickets
```

Ví dụ:

```sql
\d knowledge_chunks
```

## Xem chi tiết hơn

```sql
\d+ tickets
```

## Liệt kê extension

```sql
\dx
```

## Kiểm tra pgvector

```sql
SELECT extname, extversion
FROM pg_extension
WHERE extname = 'vector';
```

Kết quả hiện tại:

```text
vector | 0.8.6
```

## Kiểm tra kiểu vector

```sql
SELECT typname
FROM pg_type
WHERE typname = 'vector';
```

## Kiểm tra database hiện tại

```sql
SELECT current_database();
```

## Kiểm tra PostgreSQL version

```sql
SELECT version();
```

## Xem migration hiện tại

```sql
SELECT *
FROM alembic_version;
```

## Thoát psql

```sql
\q
```

---

# 10. Kiểm tra 10 bảng

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

Các bảng ứng dụng:

```text
ai_conversations
ai_messages
audit_logs
knowledge_chunks
knowledge_documents
organizations
ticket_categories
ticket_comments
tickets
users
```

Ngoài ra có:

```text
alembic_version
```

Đây là bảng Alembic quản lý version migration.

---

# 11. Kiểm tra columns của toàn bộ bảng

```sql
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

---

# 12. Kiểm tra Foreign Key

```sql
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;
```

---

# 13. Kiểm tra bảng `tickets`

```sql
\d tickets
```

Các trường quan trọng:

```text
id
organization_id
created_by
assigned_to
category_id
title
description
status
priority
ai_summary
ai_suggested_solution
ai_confidence
created_at
updated_at
resolved_at
```

---

# 14. Kiểm tra bảng `knowledge_chunks`

```sql
\d knowledge_chunks
```

Đặc biệt kiểm tra:

```text
embedding | vector(1536)
```

Kiểm tra trực tiếp:

```sql
SELECT
    column_name,
    udt_name
FROM information_schema.columns
WHERE table_name = 'knowledge_chunks'
  AND column_name = 'embedding';
```

---

# 15. Kiểm tra Docker PostgreSQL

## Container đang chạy

```powershell
docker ps
```

## Xem riêng container PostgreSQL

```powershell
docker ps --filter "name=ai-helpdesk-postgres"
```

## Xem environment của container

```powershell
docker inspect ai-helpdesk-postgres --format "{{range .Config.Env}}{{println .}}{{end}}"
```

Các giá trị hiện tại:

```text
POSTGRES_DB=ai_helpdesk
POSTGRES_USER=ai_helpdesk
POSTGRES_PASSWORD=ai_helpdesk_dev_password
```

## Kiểm tra image

```powershell
docker inspect ai-helpdesk-postgres --format "{{.Config.Image}}"
```

Hiện tại:

```text
pgvector/pgvector:pg16
```

## Xem log PostgreSQL

```powershell
docker logs ai-helpdesk-postgres
```

## Theo dõi log realtime

```powershell
docker logs -f ai-helpdesk-postgres
```

Dừng xem log:

```text
CTRL + C
```

---

# 16. Kiểm tra Docker Compose

Nếu project dùng `docker compose`:

```powershell
docker compose ps
```

Khởi động:

```powershell
docker compose up -d
```

Dừng:

```powershell
docker compose down
```

Xem log:

```powershell
docker compose logs
```

Riêng PostgreSQL:

```powershell
docker compose logs postgres
```

---

# 17. Kết nối PostgreSQL bằng DBeaver

Thông tin connection hiện tại:

```text
Database type : PostgreSQL
Host          : localhost
Port          : 5432
Database      : ai_helpdesk
Username      : ai_helpdesk
Password      : ai_helpdesk_dev_password
```

JDBC URL:

```text
jdbc:postgresql://localhost:5432/ai_helpdesk
```

Trong DBeaver có thể mở:

```text
Databases
  └── ai_helpdesk
      └── Schemas
          └── public
              └── Tables
```

Sau đó kiểm tra:

```text
tickets
users
organizations
ticket_categories
knowledge_documents
knowledge_chunks
ai_conversations
ai_messages
ticket_comments
audit_logs
```

---

# 18. Git – kiểm tra project

```powershell
git status
```

## Xem commit gần nhất

```powershell
git log --oneline -10
```

> Lệnh đúng là `--oneline`, không phải `--online`.

## Xem thay đổi

```powershell
git diff
```

## Xem file đã stage

```powershell
git diff --cached
```

## Stage

```powershell
git add .
```

## Commit

```powershell
git commit -m "Add ticket API layer"
```

## Push

```powershell
git push
```

---

# 19. Quy trình kiểm tra nhanh trước mỗi bước phát triển

Có thể dùng checklist:

```powershell
# 1. Vào backend
cd E:\Git_New\GITHUB\ai-helpdesk\backend

# 2. Kích hoạt môi trường
.\.venv\Scripts\Activate.ps1

# 3. Kiểm tra Python
python --version

# 4. Kiểm tra DB session
python -c "from app.core.database import get_db; print('get_db OK')"

# 5. Kiểm tra Models
python -c "from app.models import Base; print(sorted(Base.metadata.tables.keys()))"

# 6. Kiểm tra Alembic
alembic check

# 7. Kiểm tra Ticket Repository
python -c "from app.repositories.ticket import TicketRepository; print('TicketRepository OK')"

# 8. Kiểm tra Ticket Schemas
python -c "from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse; print('Ticket schemas OK')"

# 9. Kiểm tra Ticket Service
python -c "from app.services.ticket import TicketService; print('TicketService OK')"

# 10. Kiểm tra Ticket Router
python -c "from app.api.routes.tickets import router; print('Ticket Router OK')"

# 11. Kiểm tra routes trong OpenAPI
python -c "from app.main import app; print([p for p in app.openapi()['paths'] if 'ticket' in p])"

# 12. Chạy API
uvicorn app.main:app --reload
```

---

# 20. Quy trình PostgreSQL nhanh

Mở PowerShell:

```powershell
docker exec -it ai-helpdesk-postgres psql -U ai_helpdesk -d ai_helpdesk
```

Trong PostgreSQL:

```sql
\dt
```

```sql
SELECT current_database();
```

```sql
SELECT * FROM alembic_version;
```

```sql
SELECT extname, extversion
FROM pg_extension;
```

Kiểm tra ticket:

```sql
SELECT * FROM tickets;
```

Kiểm tra organization:

```sql
SELECT * FROM organizations;
```

Kiểm tra users:

```sql
SELECT * FROM users;
```

Thoát:

```sql
\q
```

---

# 21. Trạng thái dự án hiện tại

Đã hoàn thành:

```text
PostgreSQL + Docker             ✅
pgvector                        ✅
10 SQLAlchemy Models            ✅
Alembic                         ✅
Initial migration               ✅
Database 10 tables              ✅
DB Session                      ✅
TicketRepository                ✅
Ticket Schemas                  ✅
TicketService                   ✅
Ticket Router                   ✅
FastAPI Swagger                 ✅
```

Swagger hiện đã có:

```text
POST /api/v1/tickets
GET  /api/v1/tickets
GET  /api/v1/tickets/{ticket_id}
```

## Bước tiếp theo

```text
Seed development data
        ↓
Organization
        ↓
Users
        ↓
Ticket Categories
        ↓
POST /api/v1/tickets
        ↓
Kiểm tra Ticket trong PostgreSQL/DBeaver
```

