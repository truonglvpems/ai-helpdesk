# AI-Helpdesk Project Context

## 1. Project Identity

**Project:** AI-Helpdesk\
**Repository:** `ai-helpdesk`\
**Backend path:** `E:\Git_New\GITHUB\ai-helpdesk\backend`

### Vision

Build an enterprise AI Helpdesk platform that connects businesses with
IT resources/technicians, with AI assisting ticket classification,
summarization, suggested solutions, knowledge retrieval, and eventually
a multi-tenant marketplace model.

The long-term direction discussed for the project is similar in concept
to a platform/marketplace such as Grab or XanhSM, but for businesses and
skilled IT personnel, with AI acting as an operational assistant.

------------------------------------------------------------------------

# 2. Current Technology Stack

## Backend

-   Python 3.11
-   FastAPI
-   Uvicorn
-   SQLAlchemy
-   Alembic
-   Pydantic v2
-   JWT authentication
-   RBAC / Permission system
-   Repository / Service / Policy architecture

## Database

-   PostgreSQL
-   Docker
-   `pgvector/pgvector:pg16`
-   pgvector extension 0.8.6
-   Database: `ai_helpdesk`
-   PostgreSQL user: `ai_helpdesk`

## Development

-   Windows
-   VS Code
-   Python virtual environment: `.venv`
-   Git
-   pytest

------------------------------------------------------------------------

# 3. Existing Database / Domain Model

The project has established the following main tables/models:

-   `auth_users`
-   `users`
-   `organizations`
-   `tickets`
-   `ticket_comments`
-   `ticket_categories`
-   `knowledge_documents`
-   `knowledge_chunks`
-   `ai_conversations`
-   `ai_messages`
-   `audit_logs`

The project is designed around **Organization/Tenant isolation**.

A Ticket belongs to an Organization.

A User also belongs to an Organization.

Authenticated identity is the authoritative source for tenant identity.

------------------------------------------------------------------------

# 4. Authentication Foundation --- COMPLETED

## 10.6.4 --- JWT Authentication and RBAC Foundation

Completed and committed.

Important commit:

``` text
dcffbe5 feat(auth):10.6.4- complete JWT authentication and RBAC foundation
```

Implemented foundation includes:

-   JWT access-token authentication
-   Authentication user model
-   User profile relationship
-   `get_current_auth_user()`
-   `get_current_user()`
-   role-based authorization foundation
-   permission definitions
-   role-to-permission mapping
-   `require_role()`
-   `require_permission()`

Current dependency flow:

``` text
Bearer Token
    ↓
decode_access_token()
    ↓
AuthUser
    ↓
User
    ↓
Permission / Role authorization
```

------------------------------------------------------------------------

# 5. Ticket CRUD --- COMPLETED

Ticket CRUD API was implemented using:

``` text
Router
  ↓
Service
  ↓
Repository
  ↓
SQLAlchemy / PostgreSQL
```

Current endpoints:

``` text
POST   /api/v1/tickets
GET    /api/v1/tickets
GET    /api/v1/tickets/{ticket_id}
PATCH  /api/v1/tickets/{ticket_id}
DELETE /api/v1/tickets/{ticket_id}
```

Current FastAPI router prefix:

``` text
/tickets
```

and `main.py` includes it under:

``` text
/api/v1
```

------------------------------------------------------------------------

# 6. Ticket Tenant Identity --- COMPLETED

Ticket creation no longer trusts tenant identity supplied by the client.

`TicketService.create_ticket()` derives:

``` python
organization_id = current_user.organization_id
created_by = current_user.id
```

Therefore:

``` text
Client
  X organization_id
  X created_by

Authenticated User
  ✓ organization_id
  ✓ user id
```

The service also validates:

-   organization existence
-   creator belongs to organization
-   category belongs to organization
-   category is active

This is a fundamental multi-tenant security rule.

------------------------------------------------------------------------

# 7. Ticket Repository Tenant Scope --- COMPLETED

Commit:

``` text
7485628 fix(ticket): complete tenant scoped ticket data access
```

`TicketRepository.get_by_id()` now requires:

``` python
ticket_id
organization_id
```

and queries:

``` python
Ticket.id == ticket_id
Ticket.organization_id == organization_id
```

This prevents cross-tenant Ticket retrieval at the repository
data-access boundary.

The change also completed the schema transition so Ticket creation no
longer expects client-controlled:

``` text
organization_id
created_by
```

in `TicketCreate`.

------------------------------------------------------------------------

# 8. Ticket DELETE Tenant Scope --- COMPLETED

Milestone:

``` text
10.6.5.5D.3
```

Commit:

``` text
5403899 feat(ticket): 10.6.5.5D.3 enforce tenant scope on delete
```

Delete flow:

``` text
current_user
    ↓
current_user.organization_id
    ↓
repository.get_by_id(ticket_id, organization_id)
    ↓
same tenant → delete
other tenant → not found
```

Tests were added for:

-   delete uses current user's organization
-   cross-organization ticket cannot be deleted
-   ticket not found returns false
-   API delete behavior

------------------------------------------------------------------------

# 9. Ticket UPDATE Tenant Scope --- COMPLETED

Milestone:

``` text
10.6.5.5D.4
```

Commit:

``` text
b3cb8ce feat(ticket): 10.6.5.5D.4 enforce tenant scope on update
```

The Router now passes:

``` python
current_user
```

to:

``` python
TicketService.update_ticket()
```

The Service uses:

``` python
repository.get_by_id(
    ticket_id,
    current_user.organization_id,
)
```

Cross-tenant update is therefore blocked.

Tests cover:

-   Router passes current user
-   ticket-not-found behavior
-   current-user organization is used
-   cross-tenant update cannot occur
-   update/commit/refresh are not executed when the ticket is outside
    the tenant

------------------------------------------------------------------------

# 10. Ticket Permission Matrix / Policy --- FOUNDATION COMPLETED

A Ticket permission matrix and policy layer have been created.

Relevant permission names currently include:

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

`TicketPolicy` contains authorization methods including:

``` text
can_create()
can_read()
can_update()
can_delete()
can_assign()
can_unassign()
can_reassign()
can_comment()
can_change_status()
can_change_priority()
can_close()
can_reopen()
```

The policy checks organization scope and, where appropriate:

-   ownership
-   assignment
-   role permission

The policy layer is intentionally designed to contain authorization
rules rather than database operations or HTTP exceptions.

------------------------------------------------------------------------

# 11. Ticket Permission Wiring --- PARTIALLY COMPLETED

The project has moved from having a policy/permission definition to
actually wiring permissions into Ticket API endpoints.

## 10.6.5.5D.5.1 --- CREATE Permission --- COMPLETED

Commit:

``` text
7cb763b feat(ticket): 10.6.5.5D.5.1 enforce create permission
```

POST `/tickets` now requires:

``` text
ticket:create
```

The authenticated user remains the source of:

``` text
organization_id
created_by
```

Tests were added.

------------------------------------------------------------------------

## 10.6.5.5D.5.2 --- READ Permission --- COMPLETED

Commit:

``` text
418153a feat(ticket): 10.6.5.5D.5.2 enforce read permission
```

GET `/tickets/{ticket_id}` now requires:

``` text
ticket:read
```

Tenant scope remains enforced by the service/repository.

------------------------------------------------------------------------

## 10.6.5.5D.5.3 --- LIST + UPDATE Permission --- COMPLETED

Commit:

``` text
0e784cf feat(ticket): 10.6.5.5D.5.3 enforce list and update permissions
```

Current CRUD permission wiring is:

``` text
POST    /tickets
        → ticket:create

GET     /tickets/{ticket_id}
        → ticket:read

GET     /tickets
        → ticket:read

PATCH   /tickets/{ticket_id}
        → ticket:update

DELETE  /tickets/{ticket_id}
        → ticket:delete
```

DELETE already had its permission dependency before D.5.3.

------------------------------------------------------------------------

# 12. Current Ticket CRUD Security State

The current intended security flow is:

``` text
JWT
 ↓
Current User
 ↓
Permission
 ↓
Tenant Scope
 ↓
Ticket Service
 ↓
Repository
```

For CRUD:

``` text
CREATE
  ticket:create
  + current_user tenant identity
  + tenant/category/creator validation

READ
  ticket:read
  + tenant scoped repository lookup

LIST
  ticket:read
  + current_user.organization_id

UPDATE
  ticket:update
  + tenant scoped repository lookup

DELETE
  ticket:delete
  + tenant scoped repository lookup
```

------------------------------------------------------------------------

# 13. Tests --- CURRENT STATUS

The latest full regression result after Ticket permission wiring:

``` text
67 passed, 1 warning
```

The only warning currently reported is:

``` text
PydanticDeprecatedSince20:
Support for class-based config is deprecated.
Use ConfigDict instead.
```

This warning is known and has not yet been addressed because it is
outside the current Ticket authorization milestone.

Current tests cover:

## Dependencies

Examples:

``` text
admin has ticket delete permission
technician does not have ticket delete permission
employee has ticket create permission
employee does not have ticket delete permission
technician has ticket update permission
employee has ticket update-own permission
```

## Ticket Policy

Tests cover:

-   same-organization read
-   cross-organization read rejection
-   employee own-ticket read
-   employee other-ticket read rejection
-   delete policy
-   update policy
-   create policy
-   assignment/unassignment/reassignment
-   comments
-   status
-   priority
-   close
-   reopen
-   cross-organization restrictions

## Ticket Service

Tests cover:

-   tenant identity during creation
-   ignoring client tenant identity
-   GET tenant scope
-   UPDATE tenant scope
-   UPDATE cross-tenant rejection
-   DELETE tenant scope
-   DELETE cross-tenant rejection
-   not-found behavior

## Ticket API Routes

Tests cover:

-   LIST organization scope
-   GET organization scope
-   CREATE current-user propagation
-   UPDATE current-user propagation
-   UPDATE not-found → 404
-   DELETE current-user propagation
-   DELETE not-found → 404

------------------------------------------------------------------------

# 14. Git Checkpoint --- CURRENT HEAD

Current branch:

``` text
master
```

Current HEAD:

``` text
0e784cf
feat(ticket): 10.6.5.5D.5.3 enforce list and update permissions
```

Recent history:

``` text
0e784cf feat(ticket): 10.6.5.5D.5.3 enforce list and update permissions
418153a feat(ticket): 10.6.5.5D.5.2 enforce read permission
7cb763b feat(ticket): 10.6.5.5D.5.1 enforce create permission
b3cb8ce feat(ticket): 10.6.5.5D.4 enforce tenant scope on update
7485628 fix(ticket): complete tenant scoped ticket data access
5403899 feat(ticket): 10.6.5.5D.3 enforce tenant scope on delete
c5eec7b feat(authz): add ticket permission policy 10.6.5.5B
dcffbe5 feat(auth):10.6.4- complete JWT authentication and RBAC foundation
```

------------------------------------------------------------------------

# 15. Known Untracked Files

At the latest checkpoint, Git reports these untracked files:

``` text
../AI-HELPDESK_10.6.5.1_Ticket_Permission_Matrix.md
../Step-Ai-Helpdesk
tests/services/__init__.py
```

These were intentionally not included in the Ticket D.5.3 commit.

Their purpose/desired disposition should be reviewed separately before
adding them to Git.

------------------------------------------------------------------------

# 16. ROADMAP --- COMPLETED

## Foundation

-   [x] Project/backend foundation
-   [x] PostgreSQL + pgvector
-   [x] SQLAlchemy models
-   [x] Alembic migrations
-   [x] Organization model
-   [x] User/AuthUser model relationship
-   [x] JWT authentication
-   [x] Current-user dependency
-   [x] RBAC foundation
-   [x] Permission definitions
-   [x] Role-permission mapping

## Ticket

-   [x] Ticket model
-   [x] Ticket schema
-   [x] Ticket repository
-   [x] Ticket service
-   [x] Ticket CRUD API
-   [x] Tenant identity on CREATE
-   [x] Tenant-scoped GET
-   [x] Tenant-scoped LIST
-   [x] Tenant-scoped UPDATE
-   [x] Tenant-scoped DELETE
-   [x] Ticket permission matrix
-   [x] Ticket Policy
-   [x] CREATE permission wiring
-   [x] READ permission wiring
-   [x] LIST permission wiring
-   [x] UPDATE permission wiring
-   [x] DELETE permission wiring
-   [x] Ticket unit/service/API tests

------------------------------------------------------------------------

# 17. ROADMAP --- NOT YET COMPLETED

The following areas exist in the design/codebase but are not yet fully
wired into the operational Ticket API.

## A. Resource-level Policy Enforcement

`TicketPolicy` exists, but the current CRUD routes primarily use
`require_permission()` plus tenant-scoped data access.

Still to implement carefully:

``` text
TicketPolicy.can_read()
TicketPolicy.can_update()
TicketPolicy.can_delete()
```

where ownership/assignment-specific rules require them.

Important distinction:

``` text
Permission
    = "is this role allowed to perform this class of operation?"

Policy
    = "is this user allowed to perform this operation on THIS ticket?"
```

This distinction must be preserved.

------------------------------------------------------------------------

## B. Own / Assigned Ticket Authorization

Not yet fully integrated into the operational API flow:

``` text
ticket:read:own
ticket:read:assigned
ticket:update:own
ticket:delete:own
```

The Policy already contains logic for ownership/assignment, but the
API/service flow still needs a deliberate design for combining:

``` text
permission
+
tenant scope
+
ownership/assignment
```

Do not simply replace normal permissions with `*_own` at the Router
layer.

------------------------------------------------------------------------

## C. Ticket Assignment Authorization

Policy methods exist:

``` text
can_assign()
can_unassign()
can_reassign()
```

But assignment authorization still needs to be integrated into the
appropriate service/API operations.

Additional validation already exists in UPDATE for assigned users:

``` text
assigned user must belong to ticket organization
```

------------------------------------------------------------------------

## D. Ticket Comment Authorization

Policy exists:

``` text
can_comment()
```

and the Ticket Comments router/model area exists.

Still to complete:

-   comment permission wiring
-   tenant scope
-   ownership rule for employee comments
-   tests
-   complete authorization flow

------------------------------------------------------------------------

## E. Ticket Status / Priority Authorization

Policy methods exist:

``` text
can_change_status()
can_change_priority()
```

Still to complete operational enforcement:

-   permission dependency/service authorization
-   policy enforcement
-   state transition validation
-   tests

------------------------------------------------------------------------

## F. Ticket Close / Reopen Authorization

Policy methods exist:

``` text
can_close()
can_reopen()
```

Still to complete:

-   endpoint/service operations
-   authorization enforcement
-   ownership restrictions for employees where applicable
-   tests

------------------------------------------------------------------------

## G. Ticket State Machine / Business Rules

Ticket status currently exists and CREATE starts tickets as:

``` text
OPEN
```

A complete state machine has not yet been finalized.

Future work should define valid transitions such as:

``` text
OPEN
 ↓
IN_PROGRESS
 ↓
RESOLVED
 ↓
CLOSED
```

and reopening rules.

------------------------------------------------------------------------

## H. Audit Logs

`audit_logs` exists in the data model.

Still to integrate systematically with:

-   authentication-sensitive operations
-   Ticket creation
-   updates
-   assignment
-   status changes
-   deletion
-   comments
-   administrative actions

------------------------------------------------------------------------

## I. AI Ticket Processing

Database structures exist for:

``` text
ai_conversations
ai_messages
```

and Ticket has AI-related fields such as:

``` text
ai_summary
ai_suggested_solution
```

Still to implement:

-   AI classification
-   AI summarization
-   suggested solution generation
-   confidence scoring
-   AI conversation workflow
-   human approval/override
-   AI auditability

------------------------------------------------------------------------

## J. Knowledge Base / RAG

Models exist:

``` text
knowledge_documents
knowledge_chunks
```

and PostgreSQL/pgvector is available.

Still to implement:

-   document ingestion
-   chunking
-   embedding generation
-   vector search
-   metadata filtering by organization
-   RAG retrieval
-   answer generation
-   knowledge permissions
-   tenant-isolated knowledge search

------------------------------------------------------------------------

## K. Multi-Tenant Architecture Expansion

Ticket tenant isolation is now being enforced.

Still to expand tenant isolation consistently to:

``` text
Users
Categories
Comments
Knowledge Base
AI Conversations
AI Messages
Audit Logs
```

Every tenant-owned resource should eventually follow:

``` text
Authenticated User
       ↓
Organization Scope
       ↓
Resource Access
       ↓
Ownership / Assignment Policy
```

------------------------------------------------------------------------

## L. Admin / Organization Management

Still to develop:

-   organization administration
-   user management
-   role management
-   permission management
-   technician management
-   category management
-   organization configuration

------------------------------------------------------------------------

## M. Technician / IT Resource Marketplace

Long-term product direction, not yet implemented:

``` text
Business
   ↓
Create IT problem
   ↓
AI triage
   ↓
Internal technician
   ↓
External IT resource marketplace
   ↓
Matching
   ↓
Assignment
   ↓
Work
   ↓
Resolution
   ↓
Rating / SLA / Payment
```

This is the larger platform vision beyond the current Helpdesk MVP.

------------------------------------------------------------------------

# 18. Recommended Next Roadmap Sequence

Continue incrementally.

### Phase 1 --- Finish Ticket Authorization

``` text
10.6.5.5D.5.1  CREATE permission        [DONE]
10.6.5.5D.5.2  READ permission          [DONE]
10.6.5.5D.5.3  LIST + UPDATE permission [DONE]

Next:
10.6.5.5D.5.4  Resource-level UPDATE/READ Policy enforcement
10.6.5.5D.5.5  Assignment authorization
10.6.5.5D.5.6  Comment authorization
10.6.5.5D.5.7  Status/Priority authorization
10.6.5.5D.5.8  Close/Reopen authorization
```

The exact numbering of future steps should be confirmed against the code
at the time of implementation rather than assumed in advance.

### Phase 2 --- Ticket State and Business Rules

``` text
state transitions
assignment lifecycle
SLA
priority
comments
audit logs
```

### Phase 3 --- Knowledge Base / RAG

``` text
document ingestion
chunking
embeddings
pgvector retrieval
organization-scoped RAG
```

### Phase 4 --- AI Ticket Intelligence

``` text
classification
summarization
suggested solutions
confidence
human approval
AI audit
```

### Phase 5 --- Organization Administration

``` text
organizations
users
roles
permissions
technicians
categories
settings
```

### Phase 6 --- Marketplace / Platform

``` text
external IT resources
skill profiles
matching
availability
assignment
SLA
ratings
contracts
billing
```

------------------------------------------------------------------------

# 19. Development Rules for Continuing the Project

Use this workflow for every next milestone:

``` text
1. Inspect current code
2. Define ONE concrete change
3. Identify exact files
4. Modify only required files
5. Run focused test
6. Run relevant regression
7. Review git diff
8. git diff --check
9. Stage only intended files
10. Review staged diff
11. Commit
12. Record checkpoint
```

Do not bundle unrelated refactoring into a milestone.

Do not introduce future-step changes early.

Do not trust client-provided tenant identity.

Do not bypass repository tenant scope.

Do not confuse:

``` text
Permission
Policy
Tenant Scope
Ownership
```

These are separate authorization layers.

------------------------------------------------------------------------

# 20. Current Golden Checkpoint

The project can be resumed from:

``` text
HEAD = 0e784cf
```

Current verified regression:

``` text
67 passed, 1 warning
```

Current Ticket CRUD authorization:

``` text
CREATE  → permission + tenant scope
READ    → permission + tenant scope
LIST    → permission + tenant scope
UPDATE  → permission + tenant scope
DELETE  → permission + tenant scope
```

The next major unfinished security task is **resource-level Policy
enforcement**, especially the interaction between:

``` text
role permission
+
organization
+
ticket ownership
+
ticket assignment
```

This file is the project context checkpoint for continuing AI-Helpdesk
in a new conversation.
