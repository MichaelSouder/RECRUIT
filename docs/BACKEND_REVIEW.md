# RECRUIT Backend Review

Scope: `src/backend/app/` (FastAPI application, ~3,200 LOC), `src/backend/migrations_cli/` (ETL tooling, ~4,450 LOC), `src/backend/scripts/` (one-off maintenance scripts, ~900 LOC), and `src/backend/alembic/` (migrations). Reviewed for architecture, functionality/correctness, commenting, style, test coverage, performance, and configuration/best-practices hygiene. Frontend is out of scope (see `docs/ACTION_PLAN.md` for prior frontend findings).

This review found the codebase functionally coherent but with **one crash bug** (§1.1), a **likely second bug where assessment instrument data is silently dropped** (§7), a **material gap in the audit trail** relative to the system's own FDA 21 CFR Part 11 claims (§1.2), no automated test suite for the API (§5), a live default JWT secret (§2), missing indexes on the columns actually filtered in hot-path queries (§6), and several pieces of dead configuration — `settings.debug`/`settings.environment` and the `redis`/`redis_url` dependency are all defined and set in deployment configs but never read anywhere in the app (§7). None of the issues raised in the existing `docs/ACTION_PLAN.md` (Dec 2024) — default secret key, no rate limiting, no tests — have been addressed since it was written.

---

## 1. Correctness bugs

### 1.1 `DELETE /subjects/{id}` crashes (High)
[subjects.py:288](../src/backend/app/api/v1/subjects.py#L288) builds the pre-delete audit payload with `db_subject.gender`, but `Subject` ([subject.py](../src/backend/app/models/subject.py)) has no `gender` column — the field is named `sex`. Every call to this endpoint raises `AttributeError` after the record is already deleted from the session (post `db.delete()`/`db.commit()`), so the subject is gone but the request 500s and no audit record is written. This is a straightforward rename: `'gender': db_subject.gender` → `'sex': db_subject.sex`.

### 1.2 Audit trail doesn't cover clinical data writes (High)
`AuditService` is explicitly documented as producing "FDA-compliant audit trail entries" ([audit_service.py:10](../src/backend/app/services/audit_service.py#L10)) and `AuditLog` cites 21 CFR Part 11 ([audit_log.py:8](../src/backend/app/models/audit_log.py#L8)). In practice, coverage is inconsistent:

| Router | CREATE | UPDATE | DELETE | VIEW |
|---|---|---|---|---|
| subjects | ✅ | ✅ | ✅ | ✅ |
| studies | ✅ | ✅ | ✅ | ✅ |
| **assessments** | ❌ | ❌ | ❌ | ✅ |
| **session_notes** | ❌ | ❌ | ❌ | ✅ |
| **admin** (user CRUD, study-access grants/role changes) | ❌ | ❌ | ❌ | partial (only `GET .../studies`) |
| assessment_types | ❌ | ❌ | ❌ | ✅ |

Assessments and session notes are the actual clinical data this platform exists to protect, and their create/update/delete paths ([assessments.py:135-194](../src/backend/app/api/v1/assessments.py#L135-L194), [session_notes.py:130-189](../src/backend/app/api/v1/session_notes.py#L130-L189)) leave no trail at all. Similarly, admin actions that change who can see what data — creating/deleting users, granting/revoking/re-rolling study access ([admin.py](../src/backend/app/api/v1/admin.py)) — are unaudited except for one read endpoint. If Part 11 compliance is a real requirement (the code comments say it is), this is the top functional gap in the backend.

`AuditService.log_logout` ([audit_service.py:217](../src/backend/app/services/audit_service.py#L217)) is dead code — there's no `/logout` endpoint and no other caller.

### 1.3 PII in application logs (Medium)
`auth.py`'s `login` endpoint logs the plaintext email at every stage of the login attempt via `logging.getLogger` ([auth.py:58,62,69,71,74](../src/backend/app/api/v1/auth.py#L58)), outside the audit-log table entirely. Unlike `audit_logs`, stdout/application logs typically aren't access-controlled or retained under the same policy — this is a side channel for PII that the audit system is presumably meant to gate. Recommend dropping to `debug` level or removing the per-line email logging.

### 1.4 N+1 / repeated refresh in access checks (Low-Medium)
`_get_study_membership` and `check_study_access` call `db.refresh(current_user, ["study_memberships"])` on every invocation ([dependencies.py:85](../src/backend/app/api/dependencies.py#L85), [dependencies.py:102](../src/backend/app/api/dependencies.py#L102)). Endpoints that loop over a subject's/assessment's studies calling `check_study_access`/`check_study_write_access` per study ID (e.g. [subjects.py:127](../src/backend/app/api/v1/subjects.py#L127), [subjects.py:219](../src/backend/app/api/v1/subjects.py#L219)) issue a fresh DB round-trip per iteration. Fine at current scale, but worth collapsing into a single `db.refresh` before the loop if this becomes a hot path.

---

## 2. Security

- **Default `SECRET_KEY` ships live** ([config.py:12](../src/backend/app/config.py#L12): `"your-secret-key-change-in-production"`), and both `docker-compose.yml` and `docker-compose.prod.yml` fall back to that exact literal if the env var isn't set ([docker-compose.prod.yml:61](../docker-compose.prod.yml#L61)). Anyone who reads the repo can forge valid JWTs against any deployment that didn't override it. `docs/ACTION_PLAN.md` already flagged this in Dec 2024 (`secret_key: str  # Required, no default`); it's still unresolved. Recommend making `secret_key` a required field with no default (Pydantic will fail fast at startup if unset) and a minimum-length validator.
- **No rate limiting** on `/auth/login` or `/auth/login-piv` — unlimited password/PIV-ID guessing. Flagged in the existing action plan; still absent.
- **Mixed password-hashing dependencies**: `requirements.txt` pulls in `passlib[bcrypt]`, but `core/security.py` calls the `bcrypt` package directly and passlib is never imported in `app/`. Not a bug, but it's an unused dependency plus two ways password hashing could theoretically be done — pick one (plain `bcrypt` is fine; drop `passlib` from requirements, or migrate to `passlib.CryptContext` for algorithm-agility later).
- `python-jose` pinned at 3.3.0 and `fastapi` at 0.104.1 (Nov 2023) — both are old enough to be worth a dependency-audit pass (`pip-audit` / `safety`) given this handles clinical/PII data; not confirmed vulnerable, just stale.
- SSN is stored as an unencrypted plaintext column with only a comment acknowledging it ([subject.py:15](../src/backend/app/models/subject.py#L15): `# Should be encrypted in production`) — a comment is not a mitigation.
- No SQL-injection risk observed in `app/` — all queries go through the SQLAlchemy ORM. `migrations_cli/` uses parameterized `%s` placeholders correctly.

---

## 3. Architecture

**Layering**: `main.py` → routers (`api/v1/*.py`) → `models`/`schemas` → `database.py`, with a thin `services/` layer (just `AuditService`) and a `middleware/` layer for request-context capture. This is a conventional, easy-to-navigate FastAPI layout for a project this size — no complaint about the overall shape.

**What's missing is a shared query/authorization layer.** `get_subjects`, `get_studies`, `get_assessments`, and `get_session_notes` ([subjects.py:26-107](../src/backend/app/api/v1/subjects.py#L26-L107), [studies.py:46-106](../src/backend/app/api/v1/studies.py#L46-L106), [assessments.py:25-94](../src/backend/app/api/v1/assessments.py#L25-L94), [session_notes.py:24-88](../src/backend/app/api/v1/session_notes.py#L24-L88)) each hand-roll the same ~30 lines: study-scoped visibility filtering for non-admins, empty-result short-circuit, count-before-sort, a `sort_by`/`sort_order` if/elif ladder, and the same pagination envelope construction. Four independent copies means a bug fix or a new sort option has to be applied four times (subjects.py already accepts `sort_by=race`, others don't — that's drift, not a deliberate choice). A `paginate(query, skip, limit)` helper plus a `scope_to_accessible_studies(query, model, current_user)` helper would cut this router code by roughly a third and make the visibility rule enforceable in one place instead of four.

**Two different "list assessment types" endpoints** exist: `GET /assessments/types/list` ([assessments.py:197](../src/backend/app/api/v1/assessments.py#L197), returns distinct `assessment_type` strings actually in use) and `GET /assessment-types` ([assessment_types.py:19](../src/backend/app/api/v1/assessment_types.py#L19), the full `AssessmentType` catalog table). They answer different questions but the naming makes them look redundant; worth a comment or a rename (e.g. `/assessments/types-in-use`) so a future reader doesn't "clean up" the wrong one.

**Study-access model** (`UserStudy.study_role` plus a separate global `User.role`) is a reasonable two-tier RBAC design, and the write/manage/view distinction in `dependencies.py` ([dependencies.py:74-155](../src/backend/app/api/dependencies.py#L74-L155)) is more thought-out than the rest of the codebase — it's the best-documented part of the backend (see §4). No functional complaint here.

**`database.py`'s silent Postgres→SQLite fallback** ([database.py:9-23](../src/backend/app/database.py#L9-L23)) is worth flagging even though it's "working as intended": if Postgres is briefly unreachable at process start (e.g. container startup race), the app silently starts against a throwaway local SQLite file instead of failing loudly, which means writes during that window vanish. This looks like a dev-convenience shim that's now also live in the code path used everywhere. Consider gating it behind `settings.environment == "development"` explicitly rather than an implicit try/except.

**`migrations_cli/` is architecturally the strongest module** in the backend: consistent structured logging (`log.info("event.name", json_payload)`), parameterized SQL, config validated up front (`config.py`), and a clear command-per-file split (`etl_arc.py`, `etl_dvbic.py`, etc.). It's also 4,450 lines with zero tests, but the risk profile is different — it's a batch tool run by an operator, not a live multi-tenant API.

---

## 4. Commenting & style

- **Docstrings**: present on nearly every function, but almost uniformly one-line and restate the function name (`"""Get a single subject by ID"""` on `get_subject`). They're not wrong, just not adding information beyond the signature — low cost, low value. The exceptions that do explain *why* rather than *what* — `check_study_write_access`'s docstring on the role model ([dependencies.py:106-111](../src/backend/app/api/dependencies.py#L106-L111)), the migration-fallback comments in `config.py` ([config.py:6-7](../src/backend/app/config.py#L6-L7)) — are the most useful comments in the codebase and a good model for the rest.
- **No project-wide style tooling**: no `pyproject.toml`, `ruff.toml`, `.flake8`, or `mypy.ini` anywhere under `src/backend/`. Style is consistent by convention (4-space indent, snake_case, routers grouped by resource) but nothing enforces it, and there's no `black`/`ruff format` in CI to catch drift.
- **Import style is inconsistent**: most files import at module top, but several routers do local imports mid-function for no structural reason — `from app.models.study import Study` inside `create_subject` when `Study` isn't imported at module level despite `studies.py` importing it that way ([subjects.py:157](../src/backend/app/api/v1/subjects.py#L157)); `import logging` and `from datetime import datetime` inside function bodies in `auth.py` ([auth.py:54](../src/backend/app/api/v1/auth.py#L54)) and `session_notes.py` ([session_notes.py:114](../src/backend/app/api/v1/session_notes.py#L114), where the imported `datetime` is then unused — the format string uses `note.session_date.strftime` directly). These read like copy-paste-and-adjust rather than a deliberate pattern.
- **Duplicated validation logic**: the same email-format regex and lowercasing logic is copy-pasted across `schemas/user.py` (twice — `UserBase` and `AdminUserCreate`/`AdminUserUpdate`) and `schemas/profile.py` ([user.py:14-24,72-78,95-103](../src/backend/app/schemas/user.py#L14-L24), [profile.py:12-21](../src/backend/app/schemas/profile.py#L12-L21)). Pydantic already ships `EmailStr` (the `email-validator` package is already a dependency in `requirements.txt` but unused for this) — swapping to `EmailStr` would delete four duplicated regexes and their edge-case surface area in one move.
- **Trailing blank-line noise**: several files end with 3-5 blank lines (`audit_service.py`, `audit_log.py`, `audit.py`, `assessment_type.py`, `admin.py`) — cosmetic, but a formatter/pre-commit hook would catch it for free.
- Naming is otherwise consistent and readable throughout (routers, schemas, and models all mirror each other's field names correctly, aside from the `gender`/`sex` bug above).

---

## 5. Test coverage

**There is no automated test suite for the FastAPI application.** Confirmed by searching the whole repo:
- No `tests/` directory under `src/backend/`.
- No `conftest.py`, `pytest.ini`, or `pyproject.toml` `[tool.pytest]` section anywhere in the backend.
- `pytest` isn't in `requirements.txt`.
- The only test-shaped file, `src/backend/test_setup.py`, is a manual smoke-check script (prints ✓/✗ as it imports modules one at a time) — useful as a "did I break the environment" sanity check, not a test.
- The only real `pytest` suite in the repo is under `scripts/airgap/tests/` — it covers the air-gapped deployment CLI, not the API or data layer.

This means every finding in §1 (the `gender` crash, the audit-logging gaps) would have been caught by even a minimal integration test hitting each CRUD endpoint once. Given `docs/ACTION_PLAN.md` already scheduled "Set up pytest for backend" and "Write tests for CRUD operations" for December 2024 and neither happened, this is the highest-leverage single investment available: a `TestClient`-based suite (FastAPI ships `starlette.testclient`, already a transitive dependency) covering:

1. Auth: register/login/login-piv happy path + wrong-password/inactive-user rejection.
2. One CRUD round-trip per resource (subject, study, assessment, session note, assessment type) including the 403 paths for `check_study_access`/`check_study_write_access`/`check_study_manage_access` — these three functions encode all the access-control logic in the system and currently have zero coverage.
3. Audit-log assertions — assert a `CREATE`/`UPDATE`/`DELETE` produces exactly one `AuditLog` row with the right `entity_type`/`action`, which would make the §1.2 gaps impossible to reintroduce once fixed.

A `conftest.py` with an in-memory SQLite engine override for `get_db` (already half-supported by `database.py`'s existing SQLite fallback path) is enough to get started without standing up Postgres in CI.

---

## 6. Performance

- **Missing indexes on the columns actually being filtered on.** `Assessment.subject_id` (nullable=False), `Assessment.study_id`, `SessionNote.subject_id`, and `SessionNote.study_id` have no `index=True` ([assessment.py:10-11](../src/backend/app/models/assessment.py#L10-L11), [session_note.py:9-10](../src/backend/app/models/session_note.py#L9-L10)) even though `get_assessments`/`get_session_notes` filter on exactly these columns on every request ([assessments.py:40-50](../src/backend/app/api/v1/assessments.py#L40-L50), [session_notes.py:38-48](../src/backend/app/api/v1/session_notes.py#L38-L48)). Contrast with `study_procedures.study_id` and both `migration_events` FKs, which *do* have `index=True` — the newer tables got this right, the original four didn't. At current data volumes this won't be noticeable; it will show up as sequential scans the moment a study accumulates a few thousand assessments. Cheap to fix now via an Alembic migration, much more disruptive once these tables are large in production.
- **No connection-pool tuning.** `create_engine(database_url)` in [database.py:16,23](../src/backend/app/database.py#L16) takes SQLAlchemy's defaults (`QueuePool`, `pool_size=5`, `max_overflow=10`, no `pool_pre_ping`). Without `pool_pre_ping=True`, a connection that Postgres or a load balancer silently drops (idle timeout, container restart, network blip) surfaces as a request-time `OperationalError` instead of being transparently recycled — the standard failure mode for "backend randomly 500s once a day for no reason." Worth setting `pool_pre_ping=True` and sizing `pool_size`/`max_overflow` deliberately against expected concurrent request count once this runs behind more than a couple of Uvicorn workers.
- **Sync endpoints on a sync engine — consistent, but caps concurrency.** Every route handler across all eight routers is `def`, not `async def` ([grep confirms zero `async def` in `api/v1/`]), which is the *correct* pairing for a synchronous `psycopg2`/SQLAlchemy engine (FastAPI runs sync `def` handlers in a worker thread pool rather than blocking the event loop). This is a legitimate, deliberate-looking architectural choice, not a bug — flagging only because the thread pool has a default ceiling (Starlette defaults to 40 threads), so request concurrency is bounded by that pool rather than by the event loop. Fine for current scale; if this needs to scale beyond a moderate number of concurrent users, the options are tuning the thread pool size, running more Uvicorn worker processes, or migrating to `asyncpg`/`AsyncSession` — not an immediate action item, just worth knowing which lever to pull.
- **Pagination does a `COUNT` and a `SELECT` as two round trips** in every list endpoint ([subjects.py:69,96](../src/backend/app/api/v1/subjects.py#L69), and the equivalent in studies/assessments/session_notes). Standard and fine; a window-function count (`COUNT(*) OVER()` folded into the main query) would save one round trip per list call if this ever becomes a hot path, but it's not worth the added query complexity at current scale.

## 7. Best practices & configuration hygiene

- **`settings.debug` and `settings.environment` are dead configuration.** Both are defined in `config.py` ([config.py:26-27](../src/backend/app/config.py#L26-L27)), and both `docker-compose.yml`/`docker-compose.prod.yml` set `DEBUG=false`/`ENVIRONMENT=production` while `docker-compose.dev.yml` sets the opposite — but grepping the entire `app/` package, neither `settings.debug` nor `settings.environment` is ever read. Nothing branches on them: FastAPI's own `debug=` constructor arg is never passed in `main.py`, so the app always runs with debug tracebacks off regardless of the setting, and there's no environment-gated behavior anywhere (see next point). Either wire these through or remove them — as-is they give a false impression that the app behaves differently per environment.
- **`/docs`, `/redoc`, and `/openapi.json` are exposed unconditionally in every environment**, including whatever `docker-compose.prod.yml` runs, because nothing in `main.py` checks `settings.environment` before FastAPI auto-registers them. For a clinical data platform this is a minor information-disclosure surface (full schema of every endpoint and model, including field names like `ssn`) that's easy to close off in production: `FastAPI(docs_url=None, redoc_url=None, openapi_url=None)` when `settings.environment == "production"`.
- **Redis is configured but entirely unused.** `redis` is a pinned dependency and `redis_url` is a `Settings` field ([config.py:17](../src/backend/app/config.py#L17)), but nothing in `app/` ever imports `redis` or reads `settings.redis_url`. Either this is leftover scaffolding from a removed feature, or it's meant for the caching/session/rate-limiting work called out in `docs/ACTION_PLAN.md` and §2 above (Redis would be the natural backing store for `slowapi`-style rate limiting on `/auth/login`) — worth deciding which, since right now it's an unused service in the deployment stack and an unused dependency in the image.
- **Pydantic v1-style `class Config` is used in 7 of 8 schema modules**, while `schemas/user.py` alone uses the v2 `model_config = ConfigDict(...)` idiom ([subject.py](../src/backend/app/schemas/subject.py), [study.py](../src/backend/app/schemas/study.py), [assessment.py](../src/backend/app/schemas/assessment.py), [session_note.py](../src/backend/app/schemas/session_note.py), [assessment_type.py](../src/backend/app/schemas/assessment_type.py), [audit_log.py](../src/backend/app/schemas/audit_log.py), [user_study_access.py](../src/backend/app/schemas/user_study_access.py) vs. [user.py](../src/backend/app/schemas/user.py)). Both work under Pydantic 2.5 via its v1-compat shim, but the project has already started the v2 migration in one file and not the rest — worth finishing that pass so there's one documented convention instead of two.
- **The `Assessment.data` JSON column has no corresponding field in `AssessmentCreate`/`AssessmentUpdate`.** The model defines `data = Column(JSON, ...)` explicitly as "Flexible JSON field for assessment-specific data" ([assessment.py:17](../src/backend/app/models/assessment.py#L17)) — presumably where MoCA/DASS-21/etc. instrument-specific answers are meant to live, given `AssessmentType.fields` defines the per-instrument schema. But `schemas/assessment.py` never declares a `data` field on either input schema, and Pydantic v2 models silently drop unrecognized keys by default (no `extra="forbid"` is set anywhere). If the frontend posts a `data` payload alongside an assessment today, it is silently discarded before it reaches `Assessment(**assessment_data.model_dump())` in [assessments.py:143](../src/backend/app/api/v1/assessments.py#L143) — worth confirming against actual frontend behavior, because if so, the flexible-instrument-data feature the schema was built for doesn't currently work end-to-end.
- **No rollback path in `get_db`, and no global exception handler.** [database.py:30-36](../src/backend/app/database.py#L30-L36)'s `get_db` only closes the session in `finally`; there's no `except: db.rollback(); raise`. In practice `Session.close()` implicitly discards an uncommitted transaction, so this isn't causing data corruption today, but it means a session that hit a `DBAPIError` mid-request stays in a "pending rollback" state for the rest of that request's lifetime if anything downstream tries to use it again. Combined with the absence of any `@app.exception_handler` in `main.py`, an unhandled exception in a route just becomes a bare Starlette 500 with no structured logging of what happened — recommend adding both: an explicit rollback in `get_db`'s except path, and one global handler that logs the exception with request context before returning a generic 500.

## 8. Redis authentication (deployment hardening)

Redis currently runs **with no authentication in all four places it's deployed**, and its port is published to the host in every one of them:

| Deploy path | Redis container spec | Host port published |
|---|---|---|
| `docker-compose.yml` (default/dev) | [lines 24-37](../docker-compose.yml#L24-L37) — no `command:`, no password | `16379:6379` |
| `docker-compose.prod.yml` | [lines 39-52](../docker-compose.prod.yml#L39-L52) — identical, no password | `16379:6379` |
| `scripts/start-stack-manual.sh` (podman, manual ops) | [lines 118-124](../scripts/start-stack-manual.sh#L118-L124) — `podman run` with no `--requirepass` | `${REDIS_PUBLISH:-16379:6379}` |
| `scripts/airgap/stack.py` (`ensure_redis`, podman via `ContainerEngine`) | [lines 329-345](../scripts/airgap/stack.py#L329-L345) — `run_detached(...)` with no `command=` | `${REDIS_PUBLISH:-16379:6379}` |

Postgres, sitting right next to it in every one of these same four files, does require a username/password. Redis doesn't. Given §7 already flags Redis as an unused-but-configured dependency likely destined for rate-limiting/session use, and given the port is reachable from the host (not just the internal `recruit_network`), this is worth closing regardless of whether Redis is wired into the app yet — today, anyone who can reach the host on `16379` has unauthenticated read/write/`FLUSHALL` access to it.

### Fix — all four deploy paths, plus the two docs that quote raw `REDIS_URL`s

1. **Add a `REDIS_PASSWORD` secret**, generated and handled the same way `SECRET_KEY`/`INITIAL_ADMIN_PASSWORD` already are (env var, no default in prod, documented alongside them in `docs/AIRGAP_DEPLOY.md` and `docs/DEPLOY_PODMAN.md`).

2. **`docker-compose.yml` / `docker-compose.prod.yml`** — give the `redis` service a `command:` that turns on auth, an `environment:` entry so the CLI-based healthcheck can authenticate, and update every `REDIS_URL` to embed the password:
   ```yaml
   redis:
     image: redis:7-alpine
     container_name: recruit_redis
     command: ["redis-server", "--requirepass", "${REDIS_PASSWORD:?REDIS_PASSWORD must be set}"]
     environment:
       - REDIS_PASSWORD=${REDIS_PASSWORD:?REDIS_PASSWORD must be set}
     ports:
       - "16379:6379"
     healthcheck:
       test: ["CMD-SHELL", "redis-cli -a \"$$REDIS_PASSWORD\" --no-auth-warning ping"]
       ...
   ```
   and in `backend`'s `environment:`:
   ```yaml
   - REDIS_URL=redis://:${REDIS_PASSWORD:?REDIS_PASSWORD must be set}@redis:6379/0
   ```
   Using `${VAR:?message}` instead of `${VAR:-default}` here is deliberate — it's the same "no usable default" treatment recommended for `SECRET_KEY` in §2, and it's what actually prevents this from quietly redeploying unauthenticated if the env var is forgotten. The dev compose (`docker-compose.yml`) can still set a low-stakes local default in a `.env` file rather than at risk of leaking into prod, since it's a separate file from `docker-compose.prod.yml`.

3. **`scripts/start-stack-manual.sh`** — add a `REDIS_PASSWORD` variable alongside the existing `POSTGRES_*`/`SECRET_KEY` block near [line 48](../scripts/start-stack-manual.sh#L48), pass it to the `podman run` for redis:
   ```bash
   podman run -d \
     --name redis \
     --network "$RECRUIT_NETWORK" \
     -p "$REDIS_PUBLISH" \
     --restart unless-stopped \
     "$REDIS_IMAGE" \
     redis-server --requirepass "$REDIS_PASSWORD"
   ```
   and change the backend's `-e "REDIS_URL=redis://redis:6379/0"` ([line 136](../scripts/start-stack-manual.sh#L136)) to `-e "REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0"`.

4. **`scripts/airgap/stack.py`** — this one's the most mechanical since `ContainerEngine.run_detached` already accepts a `command=` sequence ([engine.py:190-201](../scripts/airgap/engine.py#L190-L201)):
   - Add `redis_password: str` to `StackConfig` ([stack.py:69](../scripts/airgap/stack.py#L69) area) and populate it in `build_config` from `env("REDIS_PASSWORD")`, failing fast (matching the existing `secret_key`/`initial_admin_password` treatment) if it's empty.
   - In `ensure_redis` ([stack.py:329-345](../scripts/airgap/stack.py#L329-L345)), add `command=["redis-server", "--requirepass", config.redis_password]` to the `run_detached(...)` call.
   - Change the `redis_url` default at [stack.py:182](../scripts/airgap/stack.py#L182) from `env("REDIS_URL", "redis://redis:6379/0")` to build the URL from `config.redis_password` the same way `database_url` is already assembled from `postgres_user`/`postgres_password` elsewhere in this file.
   - `_ensure_running_container`'s "exists+running → untouched" branch means an *already-running* unauthenticated Redis from a prior deploy won't be touched by a routine re-run — a one-time `podman rm -f redis` (or `--recreate-app`-style flag extended to cover redis) will be needed on any environment that's already been stood up with the old config. Worth a callout in the rollout, not just the code diff.

5. **Docs and env templates that currently show a bare `redis://redis:6379/0`** — update to show the authenticated form and where `REDIS_PASSWORD` comes from: `docs/AIRGAP_DEPLOY.md` ([line 204](../docs/AIRGAP_DEPLOY.md#L204) and its `SECRET_KEY`/`INITIAL_ADMIN_PASSWORD` callout at [line 121](../docs/AIRGAP_DEPLOY.md#L121)), `docs/DEPLOY_PODMAN.md` ([line 119](../docs/DEPLOY_PODMAN.md#L119)), `scripts/recruit-airgap.env.example` (add `REDIS_PASSWORD=` next to `REDIS_IMAGE=` at [line 30](../scripts/recruit-airgap.env.example#L30)), and `src/backend/.env.example` ([line 13](../src/backend/.env.example#L13)). `app/config.py`'s `redis_url` default ([config.py:17](../src/backend/app/config.py#L17)) should also move from a bare URL to an example that shows the `redis://:password@host:port/db` shape, so the one place the app itself reads the setting doesn't model the insecure form.

### Verification checklist ("does it still work on deploy")

Because nothing in `app/` currently reads `redis_url` (§7), there is no in-app functional path to regress — the risk is entirely in the deploy plumbing (`depends_on: redis: condition: service_healthy` gating backend startup on the healthcheck). Confirm all four paths before calling this done:

1. `docker compose up` (both `docker-compose.yml` and `docker-compose.prod.yml`) — `recruit_redis` reaches `healthy`, `recruit_backend` starts (proves the new `redis-cli -a ... ping` healthcheck string is correct and `depends_on` doesn't wedge).
2. `docker exec recruit_redis redis-cli ping` (no `-a`) → should now fail with `NOAUTH Authentication required.` — this is the actual proof the fix does something.
3. `docker exec recruit_redis redis-cli -a "$REDIS_PASSWORD" --no-auth-warning ping` → `PONG`.
4. From the host (outside the containers), `redis-cli -h 127.0.0.1 -p 16379 ping` with no password → `NOAUTH` — confirms the published port is no longer an open door.
5. Run `scripts/start-stack-manual.sh` and `scripts/airgap/stack.py` (dry-run first, then live) end to end against a clean environment, and separately against an environment with a stale unauthenticated `redis` container already running, to confirm the "exists+running → untouched" path from point 4 above is handled deliberately rather than silently leaving old deployments unauthenticated.

*(Aside, not part of this fix: `docker-compose.yml`/`docker-compose.prod.yml` also hardcode `POSTGRES_PASSWORD: postgres` rather than parameterizing it the way `scripts/start-stack-manual.sh` and `scripts/airgap/stack.py` already do — same category of issue, not in scope here since it wasn't asked for, but worth the same treatment in a follow-up.)*

---

## Priority summary

| # | Issue | Area | Effort |
|---|---|---|---|
| 1 | Fix `db_subject.gender` → `.sex` crash in `delete_subject` | Bug | Minutes |
| 2 | Confirm and fix: `Assessment.data` has no schema field, so instrument-specific JSON payloads may be silently dropped on create/update | Bug | Small |
| 3 | Add CREATE/UPDATE/DELETE audit logging to assessments, session notes, and admin user/access management | Compliance | Small |
| 4 | Require `SECRET_KEY` with no default; fail startup if unset/weak | Security | Small |
| 5 | Stand up a pytest suite (`TestClient` + SQLite) covering auth, CRUD, and access-control branches | Test coverage | Medium |
| 6 | Add indexes on `Assessment.subject_id`/`study_id` and `SessionNote.subject_id`/`study_id` | Performance | Small |
| 7 | Add rate limiting to `/auth/login` and `/auth/login-piv` (Redis is already a dependency and unused — natural backing store) | Security | Small |
| 8 | Wire `settings.environment` through: gate `/docs`/`/redoc`/`/openapi.json` off in production | Best practice | Small |
| 9 | Set `pool_pre_ping=True` and size the connection pool deliberately in `database.py` | Performance/reliability | Small |
| 10 | Extract shared pagination/sort/study-scoping helper used by 4 routers | Architecture | Medium |
| 11 | Replace hand-rolled email regex with Pydantic `EmailStr` | Style | Small |
| 12 | Standardize all schemas on Pydantic v2 `model_config = ConfigDict(...)` (currently 7 of 8 files use v1-style `class Config`) | Style | Small |
| 13 | Add explicit rollback in `get_db` + a global exception handler with logging | Best practice | Small |
| 14 | Decide fate of the unused `redis`/`redis_url` config, or wire it to rate limiting (#7) | Best practice | Small |
| 15 | **Require Redis auth (`--requirepass`) across all 4 deploy paths + published-port verification** | Security | Small-Medium |
| 16 | Add `ruff`/`black` + a minimal CI job (lint + the new test suite) | Style/process | Small |

Items 1-4 are cheap and address the report's crash bug, a possible silent-data-loss bug, and the two issues most at odds with the system's stated compliance goals. Item 5 is what prevents all of the above (and future changes) from regressing silently. Items 6-9 are the highest-value performance/best-practice fixes given current code shape — all small, all compounding in cost the longer they wait (indexes get harder to add gracefully once tables are large; unwired environment gating is easy to forget existed). Item 15 closes a currently-live exposure — an unauthenticated, host-published data store — and should be treated with the same urgency as items 1-4 despite sitting later in the list; it's numbered here by section order, not by priority.
