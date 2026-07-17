# Validation Report

Validation performed on July 17, 2026.

## Passed checks

- Python source compilation
- Ruff backend linting
- FastAPI application startup through `TestClient`
- Customer registration and JWT login
- Boutique catalogue retrieval with product variants
- Exact size-and-colour variant addition to cart
- Server-side variant stock validation
- Coupon checkout with discount cap support
- Gift-note persistence
- Order item persistence with size, colour and variant SKU
- Mock-card payment status handling
- Administrator authentication and role protection
- Revenue, product, variant and inventory dashboard API
- Collection creation API
- Product creation with multiple variants and aggregated stock
- Order workflow status update
- Alembic clean-database migration
- Strict TypeScript compilation
- Vite production frontend build
- Production npm dependency audit: zero known vulnerabilities

## Commands used

```bash
cd backend
.venv/bin/ruff check app tests
PYTHONPATH=. .venv/bin/pytest -q
DATABASE_URL=sqlite:///./migration_test.db .venv/bin/alembic upgrade head

cd ../frontend
npm run build
npm audit --omit=dev
```

## Result summary

- Backend test suite: `1 passed`
- Frontend build: passed
- Alembic migration: passed and created 12 schema tables
- Production dependency audit: `0 vulnerabilities`

## Limitation

Docker and Docker Compose files are included, but container images were not executed because a Docker daemon was unavailable in the validation environment.
