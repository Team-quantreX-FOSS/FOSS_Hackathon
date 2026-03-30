

## 🏗 System Architecture
``
          ┌─────────────┐
          │   Borrower  │
          └─────┬───────┘
                │ Registers / Inputs data
                ▼
        ┌───────────────┐
        │   Backend     │
        │ (Flask + DB)  │
        └─────┬─────────┘
   Fetch / Save │ Multi-device Sync
                ▼
          ┌─────────────┐
          │   Banker    │
          └─────┬───────┘
                │ Processes loans
                ▼
          ┌─────────────┐
          │   Admin     │
          └─────────────┘
```
