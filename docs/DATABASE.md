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