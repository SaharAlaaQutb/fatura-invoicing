# Fatura · فاتورة

**Invoicing, inventory, and reporting for small businesses.**

Fatura is a bilingual (Arabic/English) back-office application for small shops and service companies. It manages customers, products, and stock, issues professional PDF invoices, tracks partial and full payments, and produces the reports a business owner actually needs: sales, low stock, outstanding balances, and top customers.

Built as a production-quality portfolio project that demonstrates Clean Architecture, SOLID design, advanced SQL, asynchronous processing, and a polished RTL-aware React interface.

> **Project status:** the architecture and delivery blueprint are complete; the application scaffold is being implemented. Commands below describe the target developer workflow and will work once the scaffold lands.

---

## Table of contents

- [Why Fatura](#why-fatura)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech stack](#tech-stack)
- [Architecture](#architecture)
- [Domain model](#domain-model)
- [Business rules](#business-rules)
- [Getting started](#getting-started)
- [Environment variables](#environment-variables)
- [Demo data and credentials](#demo-data-and-credentials)
- [Usage](#usage)
- [API reference](#api-reference)
- [Roles and permissions](#roles-and-permissions)
- [Project structure](#project-structure)
- [Testing](#testing)
- [Internationalization](#internationalization)
- [PDF invoices and email](#pdf-invoices-and-email)
- [Deployment](#deployment)
- [Design decisions](#design-decisions)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Why Fatura

Small businesses rarely need a full ERP. They need a fast, clear tool that answers four questions:

1. Who owes me money, and how late are they?
2. What did I sell this month, and is it growing?
3. What stock is running low?
4. Can I send a professional invoice in Arabic or English right now?

Fatura answers those questions with clean data modeling, reliable money arithmetic, and a UI optimized for repetitive daily work.

---

## Features

### Catalog and customers
- Customer records with bilingual names, contact details, and preferred invoice language.
- Product catalog with unique SKU, unit price, tax rate, reorder level, and bilingual names.
- Search, filtering, sorting, and pagination.

### Inventory
- Append-only stock movements: in, out, and adjustment.
- Current stock derived from movements, never stored as a mutable field.
- Negative-stock protection (configurable).
- Low-stock report with per-product thresholds.
- Stock history per product.

### Invoicing
- Draft invoices with line items, quantities, per-line discounts, and mixed tax rates.
- Live totals in the builder; backend remains authoritative.
- Issue invoices with gap-free sequential numbering per year.
- Atomic stock deduction on issue.
- Partial and full payments with overpayment protection.
- Void issued invoices with a required reason and automatic stock restoration.
- Issued invoices are immutable; lines snapshot product data.

### Documents
- Professional A4 PDF invoices in Arabic (RTL) and English (LTR).
- Embedded Arabic font for correct glyph shaping.
- Download or email invoices asynchronously through Celery.
- Idempotent email delivery with retry and failure tracking.

### Reports and exports
- Sales by day or month with period-over-period growth using SQL window functions.
- Outstanding balances per customer with aging buckets.
- Low-stock report.
- Top customers with ranking.
- Streaming CSV export with localized headers and machine-readable values.

### Platform
- JWT authentication and three roles: owner, accountant, cashier.
- Full Arabic/English UI with RTL support and per-user language preference.
- Per-invoice language frozen at issue time.
- Keyboard-first invoice builder, accessible components, responsive layout.
- Docker Compose for one-command local development.
- GitHub Actions for lint, type checks, tests, builds, and deployment.

---

## Screenshots

Screenshots and sample documents are published with the live demo:

| Screen | English | Arabic |
|---|---|---|
| Dashboard | `docs/screenshots/dashboard-en.png` | `docs/screenshots/dashboard-ar.png` |
| Invoice builder | `docs/screenshots/builder-en.png` | `docs/screenshots/builder-ar.png` |
| Invoices list (mobile) | `docs/screenshots/invoices-mobile-en.png` | `docs/screenshots/invoices-mobile-ar.png` |
| Sample PDF | `docs/samples/invoice-en.pdf` | `docs/samples/invoice-ar.pdf` |

---

## Tech stack

| Area | Technology |
|---|---|
| Backend | Python 3.12, Django 5, Django REST Framework |
| Async | Celery, Redis |
| Database | PostgreSQL 16 |
| PDF | WeasyPrint |
| Frontend | React 18, TypeScript, Vite |
| Server state | TanStack Query |
| Forms | React Hook Form, Zod |
| UI | Tailwind CSS, shadcn/ui, TanStack Table, Recharts |
| i18n | react-i18next, Django i18n |
| Auth | djangorestframework-simplejwt |
| API docs | drf-spectacular (OpenAPI 3) |
| Infra | Docker Compose, nginx, GitHub Actions |
| Backend quality | ruff, mypy, pytest, factory_boy |
| Frontend quality | ESLint, Prettier, Vitest, React Testing Library, Playwright |

---

## Architecture

Fatura follows a pragmatic Clean Architecture. Business rules live in a framework-free domain, use cases orchestrate them, and adapters handle HTTP, persistence, PDFs, email, and exports.

### System overview

```mermaid
flowchart LR
    User[Owner / Accountant / Cashier] -->|HTTPS| SPA[React SPA]
    SPA -->|JSON / JWT| API[Django REST API]
    API --> DB[(PostgreSQL)]
    API --> Redis[(Redis)]
    Worker[Celery Worker] --> DB
    Worker --> Redis
    Worker --> SMTP[SMTP]
    API --> PDF[WeasyPrint]
    Worker --> PDF
    Nginx[nginx] --> SPA
    Nginx --> API
```

### Layers

```text
presentation/    DRF views, serializers, filters, permissions, error mapping
application/     Use cases: CreateInvoice, IssueInvoice, RecordPayment, ...
domain/          Entities, value objects, policies, errors, ports
infrastructure/  Django repositories, WeasyPrint, SMTP, CSV, Celery, clock
container.py     Composition root that wires ports to adapters
```

The dependency rule is enforced by review and import-lint conventions:

```text
presentation ──> application ──> domain
infrastructure ─> application ──> domain
container ─────> every layer
domain ────────> standard library only
```

### Request flow

```mermaid
sequenceDiagram
    participant U as User
    participant R as React
    participant V as DRF View
    participant UC as Use Case
    participant D as Domain
    participant Repo as Repository
    participant DB as PostgreSQL

    U->>R: Issue invoice
    R->>V: POST /api/invoices/{id}/issue
    V->>UC: IssueInvoice.execute(id, actor)
    UC->>D: invoice.issue(number, now)
    D-->>UC: validated transition
    UC->>Repo: save invoice + stock movements
    Repo->>DB: transaction (row locks)
    UC-->>V: InvoiceResult
    V-->>R: 200 JSON
```

### SOLID in practice

| Principle | Where it appears |
|---|---|
| Single responsibility | `Invoice` owns totals and state; `PdfRenderer` renders; `InvoiceMailer` sends; serializers only validate and translate |
| Open/closed | New tax rules are new `TaxPolicy` classes; new export formats are new `Exporter` implementations |
| Liskov substitution | `WeasyPrintPdfRenderer` and `FakePdfRenderer` are interchangeable |
| Interface segregation | Narrow ports: `InvoiceRepository`, `StockRepository`, `PdfRenderer`, `Mailer`, `Clock`, `UnitOfWork` |
| Dependency inversion | Use cases depend on protocols; `container.py` chooses implementations from settings |

### Design patterns used

- **Value Object** — `Money`, `TaxRate`, `LocalizedText`.
- **Aggregate Root** — `Invoice` guards its lines, totals, and transitions.
- **Repository** — domain-oriented persistence ports with ORM adapters.
- **Unit of Work** — one transaction per use case, with staged domain events.
- **Strategy** — `TaxPolicy`, `PdfRenderer`, `Mailer`, `Exporter`.
- **Policy** — `StockPolicy` decides whether a movement is allowed.
- **Adapter** — WeasyPrint, SMTP, CSV, Django ORM, system clock.
- **Composition Root** — a single container builds the object graph.
- **Transactional Outbox** — reliable side effects without dual writes.
- **DTO / Mapper** — application results and PDF documents are decoupled from ORM models.
- **State Machine** — explicit invoice status transitions.

---

## Domain model

```mermaid
erDiagram
    USER ||--o{ INVOICE : creates
    USER ||--o{ PAYMENT : records
    USER {
        uuid id PK
        string email
        string role
        string preferred_language
    }

    CUSTOMER ||--o{ INVOICE : receives
    CUSTOMER {
        uuid id PK
        string name_ar
        string name_en
        string email
        string phone
        string preferred_language
        bool is_active
    }

    PRODUCT ||--o{ INVOICE_LINE : referenced_by
    PRODUCT ||--o{ STOCK_MOVEMENT : has
    PRODUCT {
        uuid id PK
        string sku
        string name_ar
        string name_en
        int unit_price_minor
        string currency
        int tax_rate_bp
        int reorder_level
        bool is_active
    }

    STOCK_MOVEMENT {
        uuid id PK
        uuid product_id FK
        int quantity_delta
        string movement_type
        string reason
        string reference
        datetime occurred_at
    }

    INVOICE ||--|{ INVOICE_LINE : contains
    INVOICE ||--o{ PAYMENT : receives
    INVOICE {
        uuid id PK
        string number
        int year
        int sequence
        uuid customer_id FK
        string status
        string language
        string currency
        int subtotal_minor
        int tax_minor
        int total_minor
        datetime issued_at
        date due_at
        datetime voided_at
        string void_reason
    }

    INVOICE_LINE {
        uuid id PK
        uuid invoice_id FK
        uuid product_id FK
        string sku_snapshot
        string description_ar
        string description_en
        int quantity
        int unit_price_minor
        int discount_bp
        int tax_rate_bp
        int line_net_minor
        int line_tax_minor
    }

    PAYMENT {
        uuid id PK
        uuid invoice_id FK
        int amount_minor
        string currency
        string method
        datetime paid_at
        string reference
        string idempotency_key
    }

    INVOICE_SEQUENCE {
        int year PK
        int next_value
    }

    EMAIL_DELIVERY {
        uuid id PK
        uuid invoice_id FK
        string recipient
        string language
        string idempotency_key
        string status
        int attempts
    }

    OUTBOX_EVENT {
        uuid id PK
        string type
        json payload
        datetime created_at
        datetime processed_at
    }
```

### Money representation

Money is never a float. Every amount is stored as an integer in the currency's minor unit plus an ISO 4217 currency code.

```json
{
  "amount": 27360,
  "currency": "EGP",
  "formatted": "273.60"
}
```

Clients use `amount` and `currency` for logic; `formatted` is for display only.

### Rounding rule

For each invoice line:

```text
gross           = unit_price × quantity
discount        = round_half_up(gross × discount_rate)
net             = gross − discount
tax             = round_half_up(net × tax_rate)
line_total      = net + tax

subtotal        = Σ net
tax_total       = Σ tax
invoice_total   = subtotal + tax_total
```

Rates are stored in basis points (`1400` = 14%). Rounding happens once per line, then totals are summed.

---

## Business rules

- Stock is derived from `SUM(stock_movements.quantity_delta)`; there is no mutable stock column.
- Stock may not go negative unless `INVOICE_ALLOW_NEGATIVE_STOCK=true`.
- Only drafts can be edited.
- Issuing freezes the invoice number, language, line snapshots, and totals.
- Invoice numbers are sequential and gap-free per year (`INV-2026-000042`).
- A rolled-back issue must not consume a number.
- Payments may not exceed the outstanding balance.
- A paid invoice cannot be voided.
- Voiding requires a non-empty reason and restores stock with compensating movements.
- Issued invoice lines never change when catalog products are edited.
- Each invoice has one language, defaulted from the customer and frozen on issue.
- All money-sensitive writes run in a transaction with row locks.

---

## Getting started

### Prerequisites

- Docker Desktop (or Docker Engine + Compose v2)
- Optional for manual development: Python 3.12, Node.js 20+, PostgreSQL 16, Redis 7

### One-command local stack

```bash
git clone https://github.com/<your-org>/fatura-invoicing.git
cd fatura-invoicing

cp .env.example .env
docker compose up --build -d

docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_demo
```

Open:

| Service | URL |
|---|---|
| Web app | http://localhost:5173 |
| API | http://localhost:8000/api/ |
| API docs (Swagger UI) | http://localhost:8000/api/docs/ |
| Health check | http://localhost:8000/health/ready |

Useful commands:

```bash
docker compose logs -f backend worker
docker compose exec backend python manage.py createsuperuser
docker compose down            # stop
docker compose down -v         # stop and delete data
```

### Manual backend setup

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

export DATABASE_URL="postgres://fatura:fatura@localhost:5432/fatura"
export REDIS_URL="redis://localhost:6379/0"

python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

In a second terminal, start the worker:

```bash
cd backend
source .venv/bin/activate
celery -A config worker -l info
```

### Manual frontend setup

```bash
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

The SPA expects `VITE_API_URL` to point at the backend, for example `http://localhost:8000/api`.

---

## Environment variables

| Variable | Purpose | Example |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | Settings module | `config.settings.dev` |
| `SECRET_KEY` | Django secret key | random 64-character string |
| `DEBUG` | Debug flag | `false` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://fatura:fatura@db:5432/fatura` |
| `REDIS_URL` | Celery broker and cache | `redis://redis:6379/0` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,api.example.com` |
| `CORS_ALLOWED_ORIGINS` | Allowed SPA origins | `http://localhost:5173` |
| `DEFAULT_CURRENCY` | Default ISO currency | `EGP` |
| `DEFAULT_LOCALE` | Fallback locale | `ar` |
| `TAX_POLICY` | Tax strategy (`flat_vat`, `exempt`) | `flat_vat` |
| `PDF_RENDERER` | PDF adapter (`weasyprint`, `fake`) | `weasyprint` |
| `MAILER` | Mail adapter (`smtp`, `console`, `fake`) | `smtp` |
| `EMAIL_HOST` / `EMAIL_PORT` | SMTP server | `smtp.example.com` / `587` |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP credentials | secrets |
| `INVOICE_ALLOW_NEGATIVE_STOCK` | Allow negative stock | `false` |
| `SENTRY_DSN` | Error tracking | optional |
| `VITE_API_URL` | Frontend API base URL | `http://localhost:8000/api` |

Copy `.env.example` and never commit real secrets.

---

## Demo data and credentials

`python manage.py seed_demo` creates a realistic small business with customers, products, stock movements, invoices in different states, and payments.

| Role | Email | Password |
|---|---|---|
| Owner | `owner@fatura.local` | `ChangeMe!123` |
| Accountant | `accountant@fatura.local` | `ChangeMe!123` |
| Cashier | `cashier@fatura.local` | `ChangeMe!123` |

> These credentials are for local demonstration only. Change or disable them in any public deployment.

---

## Usage

### Create and issue an invoice

1. Sign in and open **Invoices → New**.
2. Choose a customer. The invoice language defaults to the customer's preference.
3. Add lines by searching for a product; adjust quantity and discount.
4. Watch subtotal, tax, and total update live.
5. Save the draft. Drafts can be edited later.
6. Click **Issue**. Fatura allocates the next number and deducts stock atomically.
7. Download the PDF or email it to the customer.

Keyboard shortcuts: `Enter` adds a line, `/` focuses search, `Ctrl/Cmd+S` saves the draft.

### Record a payment

1. Open an issued invoice.
2. Click **Add payment**.
3. The amount defaults to the outstanding balance.
4. Choose a method, date, and optional reference.
5. Save. The status becomes **Partially paid** or **Paid**.

### Restock a product

1. Open **Products → product detail**.
2. Click **Add stock movement**.
3. Choose in, out, or adjustment, enter the quantity, and provide a reason.
4. Save. The derived stock level and low-stock report update immediately.

### Void an invoice

1. Open an issued, unpaid invoice.
2. Click **Void**, enter a reason, and confirm.
3. Fatura restores the stock and keeps the original invoice for audit.

### API example: create, issue, and pay

```bash
# 1. Authenticate
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@fatura.local","password":"ChangeMe!123"}' \
  | jq -r '.access')

# 2. Create a draft invoice
INVOICE_ID=$(curl -s -X POST http://localhost:8000/api/invoices/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUSTOMER_UUID",
    "language": "ar",
    "due_at": "2026-11-30",
    "lines": [
      {
        "product_id": "PRODUCT_UUID",
        "quantity": 2,
        "discount_bp": 0
      }
    ]
  }' | jq -r '.id')

# 3. Issue it
curl -X POST "http://localhost:8000/api/invoices/$INVOICE_ID/issue/" \
  -H "Authorization: Bearer $TOKEN"

# 4. Record a partial payment
curl -X POST "http://localhost:8000/api/invoices/$INVOICE_ID/payments/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"amount": 10000, "currency": "EGP", "method": "cash"}'

# 5. Download the PDF
curl -L "http://localhost:8000/api/invoices/$INVOICE_ID/pdf/" \
  -H "Authorization: Bearer $TOKEN" \
  -o invoice.pdf
```

### Reports

- **Sales:** choose a period and granularity (day/month); see totals and growth percentage.
- **Outstanding:** balances per customer with 0-30, 31-60, 61-90, and 90+ day buckets.
- **Low stock:** products at or below their reorder level.
- **Top customers:** ranked by revenue for a period.
- **CSV export:** streams invoices matching the current filters; Arabic headers open correctly in Excel.

---

## API reference

All endpoints are under `/api/`. Authentication uses JWT bearer tokens.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/token/` | Obtain access and refresh tokens |
| POST | `/api/auth/token/refresh/` | Refresh an access token |
| GET/PATCH | `/api/auth/me/` | Current profile and language preference |
| GET/POST | `/api/customers/` | List or create customers |
| GET/PATCH/DELETE | `/api/customers/{id}/` | Customer detail |
| GET/POST | `/api/products/` | List or create products |
| GET/PATCH/DELETE | `/api/products/{id}/` | Product detail |
| GET/POST | `/api/products/{id}/stock-movements/` | Stock history or adjustment |
| GET/POST | `/api/invoices/` | List or create drafts |
| GET/PATCH | `/api/invoices/{id}/` | Invoice detail or draft update |
| POST | `/api/invoices/{id}/issue/` | Issue invoice and deduct stock |
| POST | `/api/invoices/{id}/payments/` | Record a payment |
| POST | `/api/invoices/{id}/void/` | Void invoice and restore stock |
| GET | `/api/invoices/{id}/pdf/` | Download the PDF |
| POST | `/api/invoices/{id}/email/` | Queue an email delivery |
| GET | `/api/reports/sales/` | Sales report with growth |
| GET | `/api/reports/low-stock/` | Low-stock report |
| GET | `/api/reports/outstanding/` | Outstanding balances and aging |
| GET | `/api/reports/top-customers/` | Top customers |
| GET | `/api/exports/invoices.csv` | Streaming CSV export |
| GET/PATCH | `/api/settings/company/` | Company profile and branding |
| GET/POST | `/api/users/` | User management (owner only) |

### Error format

```json
{
  "error": {
    "code": "invoice.insufficient_stock",
    "message": "Not enough stock for SKU-001.",
    "details": {
      "product_id": "…",
      "available": 3,
      "requested": 5
    },
    "request_id": "…"
  }
}
```

Codes are stable and machine-readable; messages are localized to the request language.

### Pagination, filtering, ordering

```http
GET /api/invoices/?status=issued&customer=<uuid>&ordering=-issued_at&page=2&page_size=25
```

Response:

```json
{
  "count": 128,
  "next": "http://localhost:8000/api/invoices/?page=3",
  "previous": "http://localhost:8000/api/invoices/?page=1",
  "results": []
}
```

---

## Roles and permissions

| Capability | Owner | Accountant | Cashier |
|---|---|---|---|
| Manage users and company settings | yes | no | no |
| Manage customers and products | yes | yes | read |
| Adjust stock | yes | yes | no |
| Create and edit drafts | yes | yes | yes |
| Issue invoices | yes | yes | yes |
| Record payments | yes | yes | yes |
| Void invoices | yes | yes | no |
| View reports and exports | yes | yes | low stock only |
| Download and email invoices | yes | yes | yes |

Permissions are enforced in use cases on the server and reflected in the UI for clarity.

---

## Project structure

```text
fatura-invoicing/
├── backend/
│   ├── config/                  Django settings, URLs, Celery
│   ├── fatura/
│   │   ├── domain/              Money, Invoice, policies, ports
│   │   ├── application/         Use cases and DTOs
│   │   ├── infrastructure/      ORM, PDF, mail, CSV, clock, tasks
│   │   ├── presentation/        DRF views, serializers, filters
│   │   ├── container.py         Composition root
│   │   └── migrations/
│   └── tests/                   unit / integration / api / factories
├── frontend/
│   └── src/
│       ├── app/                 Router, providers
│       ├── shared/              API client, auth, i18n, UI kit
│       └── features/            invoices, products, customers, reports, ...
├── deploy/                      Dockerfiles, nginx, compose
├── docs/                        ADRs, diagrams, screenshots, sample PDFs
├── scripts/                     i18n check, seed helpers
├── .github/workflows/           CI/CD
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Testing

### Backend

```bash
cd backend
ruff check .
ruff format --check .
mypy fatura
pytest --cov=fatura --cov-report=term-missing
```

- Unit tests cover money, tax, invoice state, stock policy, and use cases with in-memory fakes.
- Integration tests use real PostgreSQL for repositories, numbering concurrency, and SQL reports.
- API tests cover validation, permissions, pagination, and localized errors.

### Frontend

```bash
cd frontend
npm run lint
npm run typecheck
npm run test
npm run test:e2e
```

- Unit tests cover formatters, totals, and Zod schemas.
- Component tests cover shared components, the invoice builder, and locale switching.
- Playwright covers the create-customer → create-product → create-invoice → pay → download-PDF flow.

### Quality gates

| Metric | Target |
|---|---|
| Overall coverage | 85% |
| `domain/` and `application/` coverage | 95% |
| Lint and type errors | 0 |
| Accessibility | WCAG 2.1 AA; no serious axe violations |
| Translation key parity | 100% |

---

## Internationalization

Fatura is bilingual by design, not as an afterthought.

- **UI:** react-i18next namespaces per feature; language detection order is user profile → `localStorage` → browser → default.
- **Persistence:** the selected language is saved to the user profile and applied on every device.
- **RTL:** `<html dir="rtl">`, mirrored sidebar, logical CSS properties, and LTR runs for amounts inside Arabic text.
- **Backend:** a locale resolver reads the authenticated user's preference, then `Accept-Language`; API errors are translated while keeping stable machine codes.
- **Master data:** customers and products store Arabic and English names with fallback.
- **Invoices:** each invoice has its own language, defaulted from the customer and frozen on issue. Lines snapshot product names in that language.
- **PDF and email:** rendered in the invoice language, independent of the sender's UI language.
- **Exports:** headers follow the requester's language; values remain machine-readable.
- **Quality:** ESLint forbids literal UI strings; CI checks key and plural parity between Arabic and English.

### Adding a language

1. Add the locale to `SUPPORTED_LOCALES` in backend and frontend.
2. Add `frontend/src/shared/i18n/locales/<locale>/*.json`.
3. Add `backend/locale/<locale>/LC_MESSAGES/django.po` and compile it.
4. Add PDF and email templates for the locale, or extend the shared template.
5. Add the language to the switcher and company settings.
6. Run `npm run i18n:check` and the PDF render tests.

---

## PDF invoices and email

### PDF

- Generated on demand by `WeasyPrintPdfRenderer` behind the `PdfRenderer` port.
- Shared A4 layout with English (LTR) and Arabic (RTL) templates.
- IBM Plex Sans Arabic is embedded, so Arabic glyph shaping is correct on every machine.
- Tabular numerals keep amount columns aligned; totals align to the end side.
- Includes logo, company details, tax ID, invoice number, dates, customer block, line table, totals, notes, and payment terms.
- Generated from an immutable `InvoiceDocument` DTO, never directly from ORM models.

### Email

- `POST /api/invoices/{id}/email/` creates an `EmailDelivery` row with a unique idempotency key and enqueues a Celery task.
- The worker renders the PDF and the localized subject/body, then sends through the configured mailer.
- Duplicate tasks are no-ops; failures retry with backoff and are marked failed after the limit.
- In development, `MAILER=console` prints messages instead of sending them.

---

## Deployment

Production runs behind nginx with HTTPS:

```text
Internet → nginx (TLS, static, SPA)
              ├── /api, /admin → Gunicorn (Django)
              └── /            → React build
                          ↕
                   PostgreSQL + Redis
                          ↕
                     Celery worker
```

The GitHub Actions pipeline on `main`:

1. Runs lint, type checks, tests, migration checks, and i18n checks.
2. Builds backend and frontend images and pushes them to GHCR.
3. Connects to the VPS over SSH, pulls images, runs migrations, and restarts services.
4. Runs a smoke test against `/health/ready` and the API docs.
5. Keeps the previous image tag available for rollback.

Required production secrets: `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, SMTP credentials, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and SSH deployment keys.

---

## Design decisions

| Decision | Rationale |
|---|---|
| Integer minor units for money | Eliminates floating-point errors; deterministic totals across backend and frontend |
| Line-level half-up rounding | Simple, explainable, and matches common VAT invoicing practice |
| Issued invoices are immutable with line snapshots | Catalog edits must never alter historical documents |
| Stock derived from movements | One source of truth, full audit trail, no reconciliation bugs |
| Gap-free numbering via a locked sequence row | Meets invoice numbering expectations and survives concurrency and rollbacks |
| Transactional outbox for email | Avoids dual-write failures and duplicate sends |
| Narrow ports and a composition root | Domain and use cases stay testable without Django, Postgres, or SMTP |
| Backend is authoritative for totals | Prevents tampered or divergent client calculations; frontend mirrors rules for UX only |
| Explicit locale in use cases | Workers have no request context; PDFs and emails must render in the invoice language |
| Logical CSS properties and RTL screenshots | RTL is verified continuously, not patched at the end |
| Tabular numerals and right-aligned amounts | Accountants scan columns quickly; alignment reduces errors |
| Streaming CSV export | Keeps memory flat for large datasets |

Architectural decision records live in `docs/adr/`.

---

## Roadmap

### MVP (current scope)
- Customers, products, stock movements.
- Draft, issue, pay, and void invoices.
- Arabic and English PDFs and emails.
- Sales, low-stock, outstanding, and top-customer reports.
- CSV export, roles, JWT auth, bilingual UI.
- Docker, CI/CD, demo seed.

### After the MVP
- Credit notes and refunds.
- Multi-warehouse inventory.
- Purchase orders and supplier management.
- Recurring invoices and payment reminders.
- Full accounting ledger and tax reports.
- E-invoicing authority integrations.
- Multi-tenant organizations.
- Mobile-optimized PWA.

---

## Contributing

1. Read the architecture section and the ADRs before changing a layer boundary.
2. Create a feature branch: `feat/invoice-reminders`, `fix/rounding`, `docs/adr-011`.
3. Write tests first for domain rules and use cases.
4. Keep the dependency rule intact; do not import Django in `domain/` or `application/`.
5. Run backend and frontend quality commands locally.
6. Update OpenAPI annotations, translations, and documentation in the same PR.
7. Use clear commit messages and open a PR with a short description and test evidence.

---

## License

Released under the MIT License. Add a `LICENSE` file before publishing the repository.

---

Built with care for small businesses that deserve clean, bilingual, reliable software.
