# I -  Cấu trúc Database
ai-helpdesk/
│
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── TECH_STACK.md
│   └── DATABASE.md       ← tạo file này
│
├── frontend/
├── backend/
├── database/
├── tests/
│
├── .gitignore
└── README.md

### 1. Multi-tenant
   organizations
   users

### 2. Helpdesk
   tickets
   ticket_comments
   ticket_categories

### 3. Knowledge Base
   knowledge_documents
   knowledge_chunks

### 4. AI
   ai_conversations
   ai_messages

Organization
    │
    ├──────── Users
    │
    ├──────── Tickets
    │             │
    │             └──── Ticket Comments
    │
    └──────── Knowledge Documents
                      │
                      └──── Knowledge Chunks

# 1. Mô hình tổng thể

AI Helpdesk sẽ là multi-tenant SaaS:
User
 │
 └──── AI Conversations
             │
             └──── AI Messages

                    ┌──────────────────┐
                    │  ORGANIZATIONS   │
                    │   (Công ty)      │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
           USERS          TICKETS       KNOWLEDGE
              │              │              │
              │              ▼              ▼
              │        COMMENTS          CHUNKS
              │
              ▼
        AI CONVERSATIONS
              │
              ▼
         AI MESSAGES

# 2. Bảng organizations

Đây là bảng đại diện cho doanh nghiệp khách hàng.
organizations
────────────────────────────
id
name
slug
status
created_at
updated_at

## Ý nghĩa:
| Cột        | Kiểu      | Ý nghĩa         |
| ---------- | --------- | --------------- |
| id         | UUID      | ID công ty      |
| name       | VARCHAR   | Tên công ty     |
| slug       | VARCHAR   | Tên định danh   |
| status     | VARCHAR   | active/inactive |
| created_at | TIMESTAMP | Ngày tạo        |
| updated_at | TIMESTAMP | Cập nhật        |
Ví dụ:
id: 8a3...
name: ABC Technology
slug: abc-technology
status: active

# 3. Bảng users

Một user thuộc một organization.
users
────────────────────────────
id
organization_id
email
full_name
role
status
created_at
updated_at

## Quan hệ:
organizations
      │
      │ 1:N
      ▼
    users

## Role MVP
EMPLOYEE
IT_SUPPORT
ADMIN

## Ví dụ:
ABC Technology
│
├── Nguyen Van A
│   EMPLOYEE
│
├── Tran Van B
│   IT_SUPPORT
│
└── Admin
    ADMIN

# 4. Bảng ticket_categories

Không nên lưu category dưới dạng text tùy ý.

Tạo bảng riêng
ticket_categories
────────────────────────────
id
organization_id
name
description
is_active
created_at

##ví dụ:
Network
Hardware
Software
Email
VPN
Account
Other

Mỗi doanh nghiệp có thể có category riêng.

# 5 Bảng tickets
Đây là bảng quan trọng nhất của Helpdesk.
tickets
────────────────────────────
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

## Status
    OPEN
    IN_PROGRESS
    WAITING_USER
    RESOLVED
    CLOSED

## Priority
    LOW
    MEDIUM
    HIGH
    URGENT

## AI fields
    ai_summary
    ai_suggested_solution
    ai_confidence

## Ví dụ ticket:

    Title:
    Không kết nối được VPN

    Description:
    Tôi đang làm việc tại nhà nhưng không thể kết nối VPN.

    AI Summary:
    User không thể kết nối VPN.

    AI Suggested Solution:
    Kiểm tra VPN server và tài khoản người dùng...

    AI Confidence:
    0.91
# 6. Bảng ticket_comments

    Một ticket có nhiều comment.

    ticket_comments
    ────────────────────────────
    id
    ticket_id
    user_id
    content
    is_internal
    created_at

    Quan hệ:

    Ticket
    │
    ├── Comment
    ├── Comment
    └── Comment

    is_internal rất quan trọng.

    Ví dụ IT có thể ghi:

    "Đã kiểm tra VPN server."

    nhưng không muốn Employee nhìn thấy.

# 7. Knowledge Base

    Đây là phần tạo ra giá trị AI.

    knowledge_documents
    knowledge_documents
    ────────────────────────────
    id
    organization_id
    uploaded_by
    title
    file_name
    file_type
    file_size
    storage_path
    status
    created_at
    updated_at

    Ví dụ:

    VPN_User_Guide.pdf
    Outlook_Setup.docx
    WiFi_Manual.pdf
    IT_Policy.pdf
# 8. knowledge_chunks

    Một document sẽ được chia thành nhiều đoạn nhỏ.

    Ví dụ:

    VPN_User_Guide.pdf
        │
        ├── Chunk 001
        ├── Chunk 002
        ├── Chunk 003
        ├── Chunk 004
        └── ...

    Bảng:

    knowledge_chunks
    ────────────────────────────
    id
    document_id
    content
    chunk_index
    embedding
    created_at

    embedding sẽ sử dụng PostgreSQL + pgvector.

    Ví dụ:

    content:
    "Để kết nối VPN, người dùng phải..."

    embedding:
    [0.0123, -0.1823, 0.7234, ...]

    Sau này AI sẽ tìm những chunk có nội dung gần với câu hỏi nhất.

# 9. AI Conversation

    Không nên gắn AI trực tiếp vào ticket.

    Vì sau này Employee có thể nói chuyện với AI mà không tạo ticket.

    Tạo:

    ai_conversations
    ────────────────────────────
    id
    organization_id
    user_id
    ticket_id
    title
    created_at
    updated_at

    ticket_id có thể NULL.

    Ví dụ:

    Employee
    │
    ▼
    AI Chat
    │
    ├── Không vào VPN
    ├── Cách reset password?
    └── Cách cài Outlook?

    Nếu cần thì chuyển conversation thành ticket.

# 10. ai_messages
    ai_messages
    ────────────────────────────
    id
    conversation_id
    role
    content
    model
    tokens_input
    tokens_output
    created_at

    Role:

    USER
    ASSISTANT
    SYSTEM

    Ví dụ:

    USER:
    Tôi không vào được VPN.

    ASSISTANT:
    Hãy kiểm tra...

# 11. Toàn bộ database v1.0

    Như vậy chúng ta có:

    ┌────────────────────┐
    │   organizations    │
    └─────────┬──────────┘
            │
            ├───────────────┐
            ▼               ▼
        users         categories
            │
            ├───────────────────────┐
            ▼                       ▼
        tickets              ai_conversations
            │                       │
            ▼                       ▼
    ticket_comments          ai_messages


    organizations
        │
        ▼
    knowledge_documents
        │
        ▼
    knowledge_chunks
# 12. Nguyên tắc Multi-Tenant

    Đây là phần cực kỳ quan trọng.

    Các bảng dữ liệu nghiệp vụ phải biết nó thuộc công ty nào.

    Ví dụ:

    tickets
        organization_id

    users
        organization_id

    ticket_categories
        organization_id

    knowledge_documents
        organization_id

    ai_conversations
        organization_id

    Giả sử:

    organization_id = A

    thì user của A không bao giờ được query dữ liệu của B.

    Backend phải luôn có logic tương tự:

    WHERE organization_id = current_user.organization_id

    Không được để frontend quyết định organization_id.

    Backend phải lấy organization từ user/session đã xác thực.

    Đây là một lỗi bảo mật rất nguy hiểm nếu làm sai.

# 13. Một thay đổi tôi muốn bổ sung

    Tôi đề xuất thêm bảng:

    audit_logs
    audit_logs
    ────────────────────────────
    id
    organization_id
    user_id
    action
    entity_type
    entity_id
    metadata
    created_at

    Ví dụ:

    ADMIN
    DELETE_USER
    USER
    123

    Sau này khi doanh nghiệp hỏi:

    Ai đã xóa tài khoản này?

    chúng ta có log để kiểm tra.

# 14. Database v1.0 chính thức

    Như vậy hiện tại:

    1. organizations
    2. users
    3. ticket_categories
    4. tickets
    5. ticket_comments
    6. knowledge_documents
    7. knowledge_chunks
    8. ai_conversations
    9. ai_messages
    10. audit_logs

10 bảng là đủ cho MVP.

Không thêm Asset Management, CMDB, SLA, Change Management... vào lúc này.

# II - Database ERD + xác định chính xác kiểu dữ liệu và khóa ngoại của 10 bảng.

Được. Bây giờ chúng ta khóa Database Design v1.0 trước khi viết SQLAlchemy.

Có một điểm tôi muốn điều chỉnh so với bản trước: users không nên tự lưu password, vì chúng ta dự kiến dùng Supabase Auth. Database nghiệp vụ chỉ lưu auth_user_id để liên kết với tài khoản xác thực.

1. ERD tổng thể
┌─────────────────────┐
│   organizations     │
│─────────────────────│
│ PK id UUID          │
│    name             │
│    slug             │
│    status           │
│    created_at       │
│    updated_at       │
└──────────┬──────────┘
           │ 1
           │
     ┌─────┴──────────────────────────────────────┐
     │                                            │
     │ N                                          │ N
     ▼                                            ▼
┌─────────────────┐                    ┌─────────────────────┐
│      users      │                    │ ticket_categories   │
│─────────────────│                    │─────────────────────│
│ PK id UUID      │                    │ PK id UUID          │
│ FK org_id       │                    │ FK org_id           │
│ auth_user_id    │                    │ name                │
│ email           │                    │ description         │
│ full_name       │                    │ is_active           │
│ role            │                    │ created_at          │
│ status          │                    └──────────┬──────────┘
│ created_at      │                               │
│ updated_at      │                               │ 1
└───────┬─────────┘                               │
        │                                         │ N
        │ 1                                       ▼
        │                              ┌─────────────────────┐
        │                              │      tickets        │
        │                              │─────────────────────│
        │                              │ PK id UUID          │
        │                              │ FK org_id           │
        │                              │ FK created_by       │
        │                              │ FK assigned_to      │
        │                              │ FK category_id      │
        │                              │ title               │
        │                              │ description         │
        │                              │ status              │
        │                              │ priority            │
        │                              │ ai_summary          │
        │                              │ ai_solution         │
        │                              │ ai_confidence       │
        │                              │ created_at          │
        │                              │ updated_at          │
        │                              │ resolved_at         │
        │                              └─────────┬───────────┘
        │                                        │ 1
        │                                        │
        │                                        │ N
        │                                        ▼
        │                              ┌─────────────────────┐
        └─────────────────────────────┤ ticket_comments     │
                                       │─────────────────────│
                                       │ PK id UUID          │
                                       │ FK ticket_id       │
                                       │ FK user_id         │
                                       │ content             │
                                       │ is_internal         │
                                       │ created_at          │
                                       └─────────────────────┘


┌─────────────────────┐
│   organizations     │
└──────────┬──────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────┐
│ knowledge_documents     │
│─────────────────────────│
│ PK id UUID              │
│ FK org_id               │
│ FK uploaded_by          │
│ title                   │
│ file_name               │
│ file_type               │
│ file_size               │
│ storage_path            │
│ status                  │
│ created_at              │
│ updated_at              │
└───────────┬─────────────┘
            │ 1
            │
            │ N
            ▼
┌─────────────────────────┐
│ knowledge_chunks        │
│─────────────────────────│
│ PK id UUID              │
│ FK document_id          │
│ content                 │
│ chunk_index             │
│ embedding vector        │
│ created_at              │
└─────────────────────────┘


┌─────────────────────┐
│   organizations     │
└──────────┬──────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────┐
│  ai_conversations       │
│─────────────────────────│
│ PK id UUID              │
│ FK org_id               │
│ FK user_id              │
│ FK ticket_id NULL       │
│ title                   │
│ created_at              │
│ updated_at              │
└───────────┬─────────────┘
            │ 1
            │
            │ N
            ▼
┌─────────────────────────┐
│       ai_messages       │
│─────────────────────────│
│ PK id UUID              │
│ FK conversation_id      │
│ role                    │
│ content                 │
│ model                   │
│ tokens_input            │
│ tokens_output           │
│ created_at              │
└─────────────────────────┘


┌─────────────────────┐
│   organizations     │
└──────────┬──────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────┐
│      audit_logs         │
│─────────────────────────│
│ PK id UUID              │
│ FK org_id               │
│ FK user_id NULL         │
│ action                  │
│ entity_type             │
│ entity_id               │
│ metadata JSONB          │
│ created_at              │
└─────────────────────────┘
2. Quy ước dữ liệu

Tôi đề xuất dùng:

Loại	PostgreSQL
ID	UUID
Text ngắn	VARCHAR
Text dài	TEXT
Boolean	BOOLEAN
Ngày giờ	TIMESTAMPTZ
Số nguyên	INTEGER
Tiền	NUMERIC
JSON	JSONB
Vector AI	VECTOR

Tất cả timestamp dùng UTC.

3. organizations
organizations
Column	Type	Null	Key
id	UUID	NO	PK
name	VARCHAR(150)	NO	
slug	VARCHAR(100)	NO	UNIQUE
status	VARCHAR(20)	NO	
created_at	TIMESTAMPTZ	NO	
updated_at	TIMESTAMPTZ	NO	
Constraints
status:
ACTIVE
SUSPENDED
DELETED

slug unique toàn hệ thống.

Ví dụ:

abc-company
laurelton-vietnam
4. users
users
Column	Type	Null	Key
id	UUID	NO	PK
organization_id	UUID	NO	FK
auth_user_id	UUID	NO	UNIQUE
email	VARCHAR(255)	NO	
full_name	VARCHAR(150)	NO	
role	VARCHAR(30)	NO	
status	VARCHAR(20)	NO	
created_at	TIMESTAMPTZ	NO	
updated_at	TIMESTAMPTZ	NO	

FK:

users.organization_id
        ↓
organizations.id
Role
EMPLOYEE
IT_SUPPORT
ADMIN
Status
ACTIVE
INACTIVE
SUSPENDED

auth_user_id trỏ tới user của Supabase Auth.

Không lưu password trong bảng này.

5. ticket_categories
ticket_categories
Column	Type	Null	Key
id	UUID	NO	PK
organization_id	UUID	NO	FK
name	VARCHAR(100)	NO	
description	TEXT	YES	
is_active	BOOLEAN	NO	
created_at	TIMESTAMPTZ	NO	

FK:

organization_id → organizations.id

Nên có unique:

(organization_id, name)

Như vậy hai công ty có thể cùng có category Network.

6. tickets

Đây là bảng quan trọng nhất.

Column	Type	Null	Key
id	UUID	NO	PK
organization_id	UUID	NO	FK
created_by	UUID	NO	FK users
assigned_to	UUID	YES	FK users
category_id	UUID	YES	FK
title	VARCHAR(200)	NO	
description	TEXT	NO	
status	VARCHAR(30)	NO	
priority	VARCHAR(20)	NO	
ai_summary	TEXT	YES	
ai_suggested_solution	TEXT	YES	
ai_confidence	NUMERIC(5,4)	YES	
created_at	TIMESTAMPTZ	NO	
updated_at	TIMESTAMPTZ	NO	
resolved_at	TIMESTAMPTZ	YES	
Status
OPEN
IN_PROGRESS
WAITING_USER
RESOLVED
CLOSED
Priority
LOW
MEDIUM
HIGH
URGENT
AI confidence

Ví dụ:

0.9500
0.7200
0.3100

Constraint:

0 <= ai_confidence <= 1
7. ticket_comments
Column	Type	Null	Key
id	UUID	NO	PK
ticket_id	UUID	NO	FK
user_id	UUID	NO	FK
content	TEXT	NO	
is_internal	BOOLEAN	NO	
created_at	TIMESTAMPTZ	NO	

Quan hệ:

tickets.id
    ↓
ticket_comments.ticket_id

Xóa ticket thì có thể CASCADE comments.

8. knowledge_documents
Column	Type	Null	Key
id	UUID	NO	PK
organization_id	UUID	NO	FK
uploaded_by	UUID	NO	FK
title	VARCHAR(255)	NO	
file_name	VARCHAR(255)	NO	
file_type	VARCHAR(50)	NO	
file_size	BIGINT	NO	
storage_path	TEXT	NO	
status	VARCHAR(30)	NO	
created_at	TIMESTAMPTZ	NO	
updated_at	TIMESTAMPTZ	NO	

Status:

UPLOADED
PROCESSING
READY
FAILED
ARCHIVED
9. knowledge_chunks
Column	Type	Null	Key
id	UUID	NO	PK
document_id	UUID	NO	FK
content	TEXT	NO	
chunk_index	INTEGER	NO	
embedding	VECTOR(1536)	YES	
created_at	TIMESTAMPTZ	NO	

Lưu ý: VECTOR(1536) phụ thuộc model embedding chúng ta chọn. Tôi chưa muốn coi 1536 là cố định vĩnh viễn. Khi chốt model embedding, chúng ta sẽ khóa dimension tương ứng.

Unique:

(document_id, chunk_index)
10. ai_conversations
Column	Type	Null	Key
id	UUID	NO	PK
organization_id	UUID	NO	FK
user_id	UUID	NO	FK
ticket_id	UUID	YES	FK
title	VARCHAR(255)	YES	
created_at	TIMESTAMPTZ	NO	
updated_at	TIMESTAMPTZ	NO	

Điểm hay của thiết kế này:

ticket_id = NULL

→ cuộc hội thoại AI độc lập.

Hoặc:

ticket_id = abc...

→ AI conversation liên quan tới ticket.

11. ai_messages
Column	Type	Null	Key
id	UUID	NO	PK
conversation_id	UUID	NO	FK
role	VARCHAR(20)	NO	
content	TEXT	NO	
model	VARCHAR(100)	YES	
tokens_input	INTEGER	YES	
tokens_output	INTEGER	YES	
created_at	TIMESTAMPTZ	NO	

Role:

SYSTEM
USER
ASSISTANT

Sau này có thể thêm:

TOOL

nếu AI Agent được triển khai.

12. audit_logs
Column	Type	Null	Key
id	UUID	NO	PK
organization_id	UUID	NO	FK
user_id	UUID	YES	FK
action	VARCHAR(100)	NO	
entity_type	VARCHAR(50)	NO	
entity_id	UUID	YES	
metadata	JSONB	YES	
created_at	TIMESTAMPTZ	NO	

Ví dụ:

{
  "old_status": "OPEN",
  "new_status": "RESOLVED"
}

hoặc:

{
  "file_name": "VPN_Guide.pdf"
}
13. Foreign Keys

Tổng hợp:

users.organization_id
    → organizations.id

ticket_categories.organization_id
    → organizations.id

tickets.organization_id
    → organizations.id

tickets.created_by
    → users.id

tickets.assigned_to
    → users.id

tickets.category_id
    → ticket_categories.id

ticket_comments.ticket_id
    → tickets.id

ticket_comments.user_id
    → users.id

knowledge_documents.organization_id
    → organizations.id

knowledge_documents.uploaded_by
    → users.id

knowledge_chunks.document_id
    → knowledge_documents.id

ai_conversations.organization_id
    → organizations.id

ai_conversations.user_id
    → users.id

ai_conversations.ticket_id
    → tickets.id

ai_messages.conversation_id
    → ai_conversations.id

audit_logs.organization_id
    → organizations.id

audit_logs.user_id
    → users.id
14. Index quan trọng

Không phải cột nào cũng cần index.

MVP nên có:

users
  INDEX organization_id
  INDEX email

tickets
  INDEX organization_id
  INDEX created_by
  INDEX assigned_to
  INDEX status
  INDEX created_at

ticket_comments
  INDEX ticket_id

knowledge_documents
  INDEX organization_id
  INDEX status

knowledge_chunks
  INDEX document_id

ai_conversations
  INDEX organization_id
  INDEX user_id
  INDEX ticket_id

ai_messages
  INDEX conversation_id

audit_logs
  INDEX organization_id
  INDEX user_id
  INDEX created_at

Riêng knowledge_chunks.embedding sau này sẽ cần vector index để RAG tìm kiếm nhanh.

15. Một vấn đề bảo mật rất quan trọng

Chúng ta có:

tickets.organization_id
users.organization_id

nhưng chỉ có FK thôi chưa đủ bảo mật.

Ví dụ user A gửi request:

GET /tickets/123

Backend phải kiểm tra:

ticket.organization_id
==
current_user.organization_id

Nếu không:

Company A
    │
    └── User A
          │
          │ request ticket B
          ▼
      Company B data ❌

Sau này chúng ta sẽ xử lý ở service/repository layer, và nếu dùng Supabase/PostgreSQL trực tiếp cho một số luồng, có thể cân nhắc Row Level Security (RLS).

Đây là một trong những phần tôi muốn chúng ta thiết kế kỹ trước khi đưa sản phẩm cho doanh nghiệp.

16. Quyết định kiến trúc hiện tại

Tôi đề xuất chốt Database v1.0 với:

10 tables
+
UUID
+
PostgreSQL
+
pgvector
+
UTC timestamp
+
Multi-tenant
+
Audit log

