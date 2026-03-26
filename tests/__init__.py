"""
Mugnificent Test Suite
======================

Directory Structure:
- tests/unit/backend/     - Backend unit tests (fast, isolated)
- tests/integration/      - Integration tests (service dependencies)
- tests/e2e/api/          - API end-to-end tests
- tests/e2e/playwright/   - Browser E2E tests (Playwright)
- tests/staging/          - Staging environment configuration

Running Tests:
- pytest tests/unit/                    # Unit tests only
- pytest tests/integration/             # Integration tests only
- pytest tests/e2e/api/                 # API E2E tests
- cd tests/e2e/playwright && npx test  # Frontend E2E tests
"""
