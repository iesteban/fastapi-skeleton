# FastAPI & Pydantic Challenges

These challenges are grounded in this skeleton's architecture (models → business → presentation layers).
Each one targets a distinct concept. Work through them in order or jump to what interests you.

---

## Challenge 1 — Pydantic: Field validation and computed fields

**Goal:** Get comfortable with Pydantic v2's validation model.

Extend `CreateUserRequest` (or create a standalone model in `app/presentation/users.py`) to:

1. Add a `display_name` field that is optional and defaults to `None`.
2. Use `@field_validator` to ensure `username` contains only alphanumeric characters and underscores (reject anything else with a clear message).
3. Use `@model_validator(mode="after")` to auto-populate `display_name` from `username` if it was not supplied.
4. Add a `@computed_field` (Pydantic v2) to `UserResponse` that exposes a `profile_url: str` constructed as `/users/{id}`. 

**Key concepts:** `@field_validator`, `@model_validator`, `@computed_field`, `Field(default=...)`.

**Check your work:** instantiate the model directly in a Python shell and assert that validation errors are raised for bad usernames, and that `display_name` is filled in automatically.

---

## Challenge 2 — Routing: Query parameters, filtering, and pagination

**Goal:** Learn how FastAPI parses and validates query parameters.

Add a `GET /users/` endpoint that returns a list of users with:

1. `skip: int = 0` and `limit: int = Query(default=20, le=100)` for pagination.
2. An optional `search: str | None = None` that filters results by a case-insensitive prefix match on `username`.
3. A response model `UserListResponse` wrapping `list[UserResponse]` plus a `total: int` count.

Add the corresponding `UserService.list_users(db, skip, limit, search)` method in the business layer.

**Key concepts:** `Query()`, `le`/`ge` constraints, response model wrapping, SQLAlchemy `ilike`.

**Watch out for:** route ordering — `GET /users/{user_id}` and `GET /users/` can conflict if declared in the wrong order.

---

## Challenge 3 — Dependency injection: Reusable pagination

**Goal:** Understand how FastAPI's `Depends` system composes.

The `skip`/`limit` pattern from Challenge 2 will appear on many endpoints. Extract it into a reusable dependency:

```python
class Pagination:
    def __init__(self, skip: int = 0, limit: int = Query(default=20, le=100)):
        self.skip = skip
        self.limit = limit
```

Inject it via `pagination: Pagination = Depends()` and remove the duplicated parameters from the route signature.

Then create a second dependency `def require_api_key(x_api_key: str = Header(...))` that checks the header value against a value from `config`. Protect the `POST /users/` endpoint with it.

**Key concepts:** class-based dependencies, `Depends()`, `Header()`, chaining dependencies.

---

## Challenge 4 — Error handling: Custom exception handlers

**Goal:** Replace scattered `HTTPException` raises with a centralized error-handling layer.

Right now, `UserNotFoundError` and `UserAlreadyExistsError` are caught in the route and re-raised as `HTTPException`. Lift this out:

1. Create a structured error response model:
   ```python
   class ErrorResponse(BaseModel):
       code: str
       detail: str
   ```
2. Register exception handlers on the `FastAPI` app in `create_app()` using `@app.exception_handler(UserNotFoundError)` (and the same for `UserAlreadyExistsError`).
3. Remove the `try/except` blocks from the route handlers entirely.
4. Use `responses={404: {"model": ErrorResponse}}` in the route decorator to document the error shape in OpenAPI.

**Key concepts:** `app.exception_handler`, `JSONResponse`, OpenAPI `responses` documentation.

---

## Challenge 5 — Pydantic: Nested models and partial updates

**Goal:** Model a PATCH (partial update) endpoint properly.

Add `PATCH /users/{user_id}` that allows updating `username` and/or `email` independently.

1. Create `UpdateUserRequest` where every field is optional:
   ```python
   class UpdateUserRequest(BaseModel):
       username: str | None = Field(default=None, min_length=3, max_length=50)
       email: EmailStr | None = None
   ```
2. Use `model.model_dump(exclude_unset=True)` to detect which fields were actually sent (vs. omitted). Apply only those to the DB row.
3. Add `UserService.update_user(db, user_id, **fields)` in the business layer.
4. Return `UserResponse` from the endpoint.

**Key concepts:** `exclude_unset=True`, partial updates, difference between `None` default and field not sent.

---

## Challenge 6 — Middleware: Request timing

**Goal:** Learn how middleware intercepts every request/response cycle.

Add a middleware in `create_app()` that:

1. Records `time.perf_counter()` before the request is processed.
2. Calls `await call_next(request)`.
3. Adds an `X-Process-Time` response header with the elapsed milliseconds.

```python
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    ...
```

**Bonus:** Add a `RequestID` middleware that generates a UUID per request, stores it on `request.state.request_id`, and echoes it back in an `X-Request-ID` response header.

**Key concepts:** `@app.middleware("http")`, `call_next`, `request.state`, `response.headers`.

---

## Challenge 7 — Background tasks: Async side effects

**Goal:** Offload work that doesn't need to block the HTTP response.

After a user is created, "send a welcome email" (just log to stdout for now) without making the client wait for it.

1. Inject `BackgroundTasks` into `POST /users/`.
2. Write `def send_welcome_email(username: str, email: str)` as a plain function.
3. Call `background_tasks.add_task(send_welcome_email, ...)` before returning the response.

**Bonus:** Write a test that confirms the function was called — use `unittest.mock.patch` to mock it and assert `call_count == 1`.

**Key concepts:** `BackgroundTasks`, fire-and-forget, testing background tasks.

---

## Challenge 8 — Testing: Mocking dependencies

**Goal:** Write fast unit-level tests for route handlers without hitting the database.

Look at `tests/test_presentation/test_users_mocked.py`. The pattern is to override `get_db` with a mock session. Extend this:

1. Write a test for the `PATCH /users/{user_id}` endpoint from Challenge 5 that:
   - Mocks `UserService.update_user` to return a fake `User`.
   - Asserts the response body matches `UserResponse`.
   - Asserts the service was called with the right arguments.
2. Write a test that verifies the `409` response when `UserAlreadyExistsError` is raised (or the `404` for `UserNotFoundError` after Challenge 4).

Use `unittest.mock.patch` or `pytest-mock`'s `mocker` fixture.

**Key concepts:** `dependency_overrides`, `unittest.mock.patch`, isolating HTTP layer from business layer.

---

## Challenge 9 — Lifespan and startup state: A simple in-memory cache

**Goal:** Understand how to attach shared state to the app using the lifespan pattern.

Add a naive in-memory cache for `GET /users/{user_id}`:

1. Create a `dict` that lives on `app.state.user_cache` — initialize it in the `lifespan` function inside `create_app()`.
2. In the route handler, check the cache before querying the DB; populate it on a miss.
3. In `PATCH /users/{user_id}` and any delete endpoint, invalidate the cache entry.
4. Inject `request: Request` into the route to access `request.app.state.user_cache`.

**Note:** This is intentionally simplistic. The point is to practice the lifespan/state pattern, not to build a production cache.

**Key concepts:** `lifespan`, `app.state`, `Request`, cache invalidation basics.

---

## Challenge 10 — OpenAPI customization and response models

**Goal:** Make the auto-generated docs accurate and useful.

1. Give the `FastAPI` app a `title`, `version`, and `description` in `create_app()`.
2. Add `summary` and `description` to each route decorator.
3. Create a `DeleteResponse` model `{"message": str}` and use it as the `response_model` for a `DELETE /users/{user_id}` endpoint.
4. Add `response_model_exclude` or `response_model_include` to an endpoint to strip a field from the output without changing the underlying Pydantic model.
5. Visit `/docs` and `/redoc` — verify every endpoint has correct status codes, request/response schemas, and descriptions.

**Key concepts:** `response_model`, `response_model_exclude`, OpenAPI metadata, Swagger UI.

---

## Tips

- Run the dev server with `python run.py` and explore `/docs` after each challenge.
- Tests live in `tests/`; run them with `pytest`.
- The `db` and `client` fixtures in `conftest.py` give you an isolated SQLite session per test.
- For Flask/Django folks: FastAPI's dependency injection replaces `g`, `request` context locals, and Django's middleware class pattern — it's explicit and composable.
