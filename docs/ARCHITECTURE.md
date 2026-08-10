                    User
                      │
                      ▼
                ┌───────────┐
                │ Next.js   │
                │ Frontend  │
                └─────┬─────┘
                      │
                   REST API
                      │
                      ▼
                ┌───────────┐
                │ FastAPI   │
                │ Backend   │
                └─────┬─────┘
                      │
          ┌───────────┼────────────┐
          │           │            │
          ▼           ▼            ▼
    PostgreSQL     Storage       AI API
          │                        │
          ▼                        ▼
       pgvector                 LLM