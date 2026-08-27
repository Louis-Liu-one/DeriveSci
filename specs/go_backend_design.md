# Go backend migration

## Requirements

While an existing DeriveSci browser client sends requests to a current `/api/...` path, the system shall preserve that path and its form or JSON request format.

While a user is logged in, when the user changes data, the system shall verify the signed session, CSRF token, input limits, and resource ownership before writing to the database.

While the service starts with no database, the system shall create a SQLite schema compatible with the original Flask tables.

## Architecture

- Frontend: existing static assets remain at `/static/`; Go renders minimal server pages and returns API JSON in the format expected by existing browser code.
- Backend: a `net/http` server uses parameterized `database/sql` queries and SQLite. Routes are grouped by user, problem, article, social, image, and help handlers.
- Security: sessions use signed, HttpOnly, SameSite=Lax cookies. State-changing endpoints use gorilla/csrf. Handlers enforce login, ownership, administrator checks, body limits, uploads limited to images, and explicit public fields.

## Implementation plan

- [x] Map Flask routes, data tables, and browser request formats.
- [ ] Create Go configuration and SQLite store.
- [ ] Add session, CSRF, authorization, and HTTP hardening middleware.
- [ ] Implement API handlers.
- [ ] Add page routes and operational documentation.
- [ ] Add tests and run the build.
