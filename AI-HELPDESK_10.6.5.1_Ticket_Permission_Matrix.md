# AI-Helpdesk --- 10.6.5.1 Thiết kế ma trận quyền Ticket

**Project:** AI-Helpdesk\
**Phase:** 10.6.5 --- Ticket Authorization\
**Step:** 10.6.5.1 --- Thiết kế ma trận quyền Ticket\
**Status:** DESIGN COMPLETED\
**Previous milestone:** 10.6.4 --- JWT Authentication + RBAC foundation\
**Git baseline:**
`dcffbe5 feat(auth):10.6.4- complete JWT authentication and RBAC...`

------------------------------------------------------------------------

## 1. Mục tiêu

Xác định chính xác:

> Ai được phép thực hiện hành động nào trên Ticket nào, trong
> Organization nào?

Thiết kế phải hỗ trợ:

-   JWT Authentication đã có.
-   RBAC.
-   Multi-tenant / Organization scope.
-   Resource ownership.
-   Ticket assignment.
-   Mở rộng sau này sang marketplace IT giữa doanh nghiệp và Technician.

**Nguyên tắc:** chưa triển khai code authorization trong bước này; chỉ
chốt thiết kế.

------------------------------------------------------------------------

## 2. Các Role chính

  Role            Phạm vi
  --------------- --------------------------------------
  `SUPER_ADMIN`   Toàn hệ thống
  `ORG_ADMIN`     Trong một Organization
  `TECHNICIAN`    Ticket thuộc phạm vi được phép xử lý
  `USER`          Ticket do chính mình tạo

Các role mở rộng như `SENIOR_TECHNICIAN`, `IT_MANAGER`, `AUDITOR`,
`AI_AGENT`, `EXTERNAL_TECHNICIAN` chưa triển khai ở bước này.

------------------------------------------------------------------------

## 3. Ticket Actions

Các hành động được chuẩn hóa:

``` text
CREATE
READ
UPDATE
DELETE
ASSIGN
UNASSIGN
REASSIGN
COMMENT
CHANGE_STATUS
CHANGE_PRIORITY
CLOSE
REOPEN
```

CRUD không đại diện cho toàn bộ authorization. Ví dụ
`PATCH /tickets/{id}` không có nghĩa mọi role đều được sửa mọi field.

------------------------------------------------------------------------

## 4. Ma trận quyền cấp nghiệp vụ

  Action             SUPER_ADMIN   ORG_ADMIN          TECHNICIAN              USER
  ----------------- ------------- ----------- -------------------------- ---------------
  Create                 YES          YES                YES                   YES
  List                   All          Org      Assigned / allowed scope        Own
  Read                   All          Org              Relevant                Own
  Update                 YES          YES              Relevant           Own / limited
  Delete                 YES          YES                 NO              Own / policy
  Assign                 YES          YES               Policy                 NO
  Unassign               YES          YES               Policy                 NO
  Reassign               YES          YES               Policy                 NO
  Comment                YES          YES                YES              Own / allowed
  Change Status          YES          YES                YES                 Limited
  Change Priority        YES          YES               Policy                 NO
  Close                  YES          YES                YES                   NO
  Reopen                 YES          YES               Policy               Limited

`Policy` và `Own / limited` phải được triển khai thành các rule cụ thể ở
các bước authorization tiếp theo.

------------------------------------------------------------------------

## 5. Resource Scope

Ticket phải được đánh giá dựa trên các thuộc tính:

``` text
ticket.organization_id
ticket.created_by
ticket.assigned_to
ticket.status
```

### USER

``` text
ticket.organization_id == current_user.organization_id
AND
ticket.created_by == current_user.id
```

### TECHNICIAN

``` text
ticket.organization_id == current_user.organization_id
AND
(
    ticket.assigned_to == current_user.id
    OR
    technician_has_org_ticket_access
)
```

### ORG_ADMIN

``` text
ticket.organization_id == current_user.organization_id
```

### SUPER_ADMIN

``` text
all organizations
```

------------------------------------------------------------------------

## 6. Permission không đồng nghĩa với Access

Ví dụ `TECHNICIAN` có permission:

``` text
ticket:read
```

không có nghĩa Technician được đọc mọi Ticket trên toàn hệ thống.

Authorization cuối cùng phải kiểm tra:

``` text
Permission
+
Organization Scope
+
Resource Ownership
+
Assignment
+
Ticket State
```

Mô hình:

``` text
JWT
  ↓
Current User
  ↓
Role
  ↓
Permission
  ↓
Ticket Policy
  ├── Organization
  ├── Ownership
  ├── Assignment
  └── State
  ↓
ALLOW / DENY
```

------------------------------------------------------------------------

## 7. Permission Naming Convention

Permission được chuẩn hóa theo dạng:

``` text
ticket:create
ticket:read
ticket:read:own
ticket:read:assigned
ticket:update
ticket:update:own
ticket:delete
ticket:delete:own
ticket:assign
ticket:unassign
ticket:reassign
ticket:comment
ticket:change_status
ticket:change_priority
ticket:close
ticket:reopen
```

Không hard-code role check trực tiếp trong từng endpoint.

Không nên sử dụng:

``` python
if current_user.role == "ADMIN":
    ...
```

rải rác trong router/service.

Thay vào đó:

``` text
Role
  ↓
Permission
  ↓
Policy
```

------------------------------------------------------------------------

## 8. Mapping Role → Permission ở mức thiết kế

### SUPER_ADMIN

``` text
*
```

Có quyền toàn hệ thống.

### ORG_ADMIN

``` text
ticket:create
ticket:read
ticket:update
ticket:delete
ticket:assign
ticket:unassign
ticket:reassign
ticket:comment
ticket:change_status
ticket:change_priority
ticket:close
ticket:reopen
```

Scope vẫn giới hạn bởi Organization.

### TECHNICIAN

``` text
ticket:create
ticket:read
ticket:update
ticket:comment
ticket:assign       # subject to policy
ticket:unassign     # subject to policy
ticket:reassign     # subject to policy
ticket:change_status
ticket:change_priority
ticket:close
ticket:reopen
```

Scope phụ thuộc Organization + Assignment / Ticket Policy.

### USER

``` text
ticket:create
ticket:read:own
ticket:update:own
ticket:comment
ticket:change_status   # limited policy
ticket:reopen          # limited policy
```

------------------------------------------------------------------------

## 9. Authorization Architecture

Kiến trúc mục tiêu:

``` text
HTTP Request
    ↓
JWT Authentication
    ↓
Current Auth User
    ↓
Role / Permission
    ↓
Ticket Authorization Policy
    ↓
Ticket Service
    ↓
Ticket Repository
    ↓
PostgreSQL
```

Dự kiến cấu trúc:

``` text
app/
├── api/
│   └── routes/
│       └── tickets.py
├── core/
│   ├── jwt.py
│   └── security.py
├── policies/
│   └── ticket.py
├── services/
│   └── ticket.py
└── repositories/
    └── ticket.py
```

`policies/ticket.py` chịu trách nhiệm kiểm tra các action trên Ticket.

------------------------------------------------------------------------

## 10. Ticket Policy dự kiến

Các policy function chính:

``` python
can_create_ticket()
can_read_ticket()
can_update_ticket()
can_delete_ticket()
can_assign_ticket()
can_unassign_ticket()
can_reassign_ticket()
can_comment_ticket()
can_change_status()
can_change_priority()
can_close_ticket()
can_reopen_ticket()
```

Policy không nên thực hiện database CRUD trực tiếp.

Policy trả lời:

``` text
ALLOW
hoặc
DENY
```

Service chịu trách nhiệm nghiệp vụ; Repository chịu trách nhiệm
persistence.

------------------------------------------------------------------------

## 11. Multi-Tenant Rule

Đây là rule bắt buộc:

> User không được truy cập Ticket của Organization khác chỉ vì biết
> `ticket_id`.

Do đó mọi thao tác Ticket phải kiểm tra Organization scope trước khi cho
phép resource access.

Ví dụ:

``` text
GET /api/v1/tickets/{ticket_id}
```

không được chỉ làm:

``` python
ticket = repository.get(ticket_id)
```

mà phải đảm bảo:

``` text
authenticated user
        +
organization scope
        +
ticket policy
        ↓
ALLOW / 404 / 403
```

------------------------------------------------------------------------

## 12. Future Marketplace Compatibility

Thiết kế này phải cho phép mở rộng sau này:

``` text
Organization
      │
      └── Ticket
             │
             ├── Internal Technician
             │
             └── External Technician
```

External Technician có thể được cấp quyền theo:

``` text
Organization
+
Ticket
+
Assignment
+
Permission
+
Time / Status Policy
```

Vì vậy không thiết kế authorization chỉ dựa trên Role.

Kiến trúc dài hạn:

``` text
RBAC
 +
Resource-Based Authorization
 +
ABAC / Policy
```

------------------------------------------------------------------------

## 13. Roadmap sau 10.6.5.1

``` text
10.6.5.1 — Thiết kế ma trận quyền Ticket       DONE
        ↓
10.6.5.2 — Chuẩn hóa Permission constants
        ↓
10.6.5.3 — Ticket Authorization Policy
        ↓
10.6.5.4 — RBAC Dependency
        ↓
10.6.5.5 — Organization / Tenant Scope
        ↓
10.6.5.6 — Áp quyền vào Ticket CRUD
        ↓
10.6.5.7 — Authorization Test Matrix
        ↓
10.6.5.8 — Commit 10.6.5
```

------------------------------------------------------------------------

## 14. Definition of Done --- 10.6.5.1

Bước 10.6.5.1 được coi là hoàn thành khi:

-   [x] Xác định Role chính.
-   [x] Xác định Ticket actions.
-   [x] Xây dựng ma trận Role × Action.
-   [x] Xác định Organization scope.
-   [x] Xác định ownership.
-   [x] Xác định assignment.
-   [x] Tách Permission khỏi Role.
-   [x] Xác định permission naming convention.
-   [x] Xác định Ticket Policy architecture.
-   [x] Đảm bảo thiết kế hỗ trợ multi-tenant.
-   [x] Đảm bảo có khả năng mở rộng sang marketplace Technician.

------------------------------------------------------------------------

## 15. Quyết định kiến trúc đã chốt

**Authorization của AI-Helpdesk không chỉ là RBAC.**

Thiết kế chính thức:

``` text
JWT Authentication
        ↓
Current User
        ↓
RBAC / Permission
        ↓
Organization Scope
        ↓
Resource Ownership / Assignment
        ↓
Ticket State Policy
        ↓
ALLOW / DENY
```

Đây là baseline bắt buộc cho toàn bộ các bước authorization Ticket tiếp
theo.
