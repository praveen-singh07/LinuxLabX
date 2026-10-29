# LinuxLabX Architecture

> **Document status:** Current architecture reference\
> **Scope:** Architecture and implementation that has been established
> for LinuxLabX\
> **Important:** This document separates implemented architecture from
> planned architecture. It does not treat future features as current
> components.

------------------------------------------------------------------------

## 1. Architecture Overview

LinuxLabX is a Python-based web application for interactive Linux
learning. The established stack is:

-   **Backend:** Python + FastAPI
-   **ORM / data access:** SQLAlchemy
-   **Validation / API schemas:** Pydantic
-   **Database:** SQLite
-   **Server-side HTML rendering:** Jinja2
-   **Frontend:** HTML, CSS3, Vanilla JavaScript
-   **Authentication:** JWT
-   **Development server:** Uvicorn
-   **Version control:** Git / GitHub

The application follows a **layered modular-monolith architecture**.

The established dependency direction is:

``` text
Browser
   |
   v
FastAPI Routes / API Layer
   |
   v
Pydantic Schemas
   |
   v
Service / Business Logic Layer
   |
   v
SQLAlchemy ORM / Data Access
   |
   v
SQLite
```

The frontend remains a server-rendered HTML application enhanced with
Vanilla JavaScript. It is not based on React, Vue, Angular, or another
frontend framework.

The architecture is intentionally modular so that learning,
authentication, gamification, and other application areas can be
expanded without moving core business logic into browser-side
JavaScript.

------------------------------------------------------------------------

## 2. High-Level System Diagram

The current architecture can be represented as follows:

``` mermaid
flowchart TD
    U[User / Browser]

    FE[HTML + CSS3 + Vanilla JavaScript]
    RT[FastAPI Routes / API Layer]
    SC[Pydantic Schemas]
    SV[Service / Business Logic Layer]
    ORM[SQLAlchemy ORM]
    DB[(SQLite Database)]

    U --> FE
    FE --> RT
    RT --> SC
    SC --> SV
    SV --> ORM
    ORM --> DB

    DB --> ORM
    ORM --> SV
    SV --> RT
    RT --> FE
    FE --> U
```

This diagram describes the established architectural direction. It does
not imply that every planned LinuxLabX feature already has an
implemented route, service, schema, or model.

------------------------------------------------------------------------

## 3. Architectural Style

LinuxLabX currently uses a **modular monolith** rather than a
microservice architecture.

### Characteristics

-   One FastAPI application.
-   Clear separation between API/routing, validation, business logic,
    ORM models, templates, and static assets.
-   SQLite is used as the current development database.
-   SQLAlchemy provides the database abstraction.
-   Jinja2 is used for dynamic HTML rendering.
-   Vanilla JavaScript handles browser-side interaction.
-   Authentication uses JWT.
-   The architecture is designed to allow future features to be added as
    modules rather than by creating unrelated implementations.

The project is not currently split into independently deployed services.

------------------------------------------------------------------------

# 4. Frontend Architecture

## 4.1 Technologies

The established frontend technologies are:

-   HTML
-   CSS3
-   Vanilla JavaScript
-   Jinja2 for server-side dynamic HTML rendering

No frontend framework is part of the current architecture.

## 4.2 Responsibilities

The frontend is responsible for:

-   Presenting application pages and learning content.
-   Providing forms and user interactions.
-   Rendering server-provided data through Jinja2 templates.
-   Performing client-side interaction through Vanilla JavaScript.
-   Sending requests to backend endpoints when browser-side interaction
    requires backend communication.
-   Displaying validation or operation results returned by the backend.

The frontend is **not** responsible for:

-   Direct database access.
-   SQLAlchemy operations.
-   Password hashing.
-   JWT creation.
-   Core business rules.
-   Server-side authorization decisions.
-   Executing real Linux commands in the current V1 architecture.

## 4.3 Frontend principle

Business logic should remain on the backend.

Vanilla JavaScript may control presentation and browser interaction, but
it must not become an alternative backend service layer.

------------------------------------------------------------------------

# 5. Backend Architecture

The backend is built with Python and FastAPI.

The established backend layers are:

``` text
api
  ↓
schemas
  ↓
services
  ↓
models / SQLAlchemy
  ↓
SQLite
```

The exact responsibility of each area is kept separate so that routes do
not become large blocks containing validation, business rules, and
database operations together.

------------------------------------------------------------------------

# 6. FastAPI Routing / API Layer

The `api` area contains the application's HTTP-facing routes.

Routes are responsible for:

-   Receiving HTTP requests.
-   Connecting request data with Pydantic schemas.
-   Calling the appropriate application/service logic.
-   Returning HTTP responses.
-   Returning appropriate status codes for established operations.
-   Using FastAPI dependency injection where applicable.

Routes should remain **thin**.

A route should not become the location for:

-   Complex business rules.
-   Repeated database logic.
-   Password hashing implementation.
-   Large authentication algorithms.
-   Direct frontend presentation logic.

The API layer is the boundary between HTTP requests and the application
logic.

------------------------------------------------------------------------

# 7. Service / Business-Logic Layer

The `services` area is intended for application and business logic.

The purpose of the service layer is to prevent business rules from being
embedded directly inside route functions.

For example, authentication-related application logic includes concepts
such as:

-   Looking up a user.
-   Checking whether an email already exists.
-   Hashing a password before persistence.
-   Verifying a password during login.
-   Creating an authentication token.

The service layer works with SQLAlchemy/database objects rather than
making the browser responsible for these operations.

### Service-layer rules

Services may:

-   Apply business rules.
-   Coordinate database operations.
-   Use SQLAlchemy models.
-   Perform application-level calculations and decisions.
-   Support route handlers.

Services should not:

-   Render HTML directly as their primary responsibility.
-   Read HTTP request details unnecessarily.
-   Put browser-specific JavaScript behavior into backend code.
-   Bypass the established data-access architecture without a reason.

------------------------------------------------------------------------

# 8. SQLAlchemy Model / Data-Access Layer

SQLAlchemy is the ORM used by LinuxLabX.

The established model layer is represented by the `models` area.

SQLAlchemy provides the mapping between Python model classes and
database tables.

The current database architecture uses:

``` text
Python application
       |
       v
SQLAlchemy ORM
       |
       v
SQLite database file
```

The application uses a SQLAlchemy `Session` for database operations.

A database dependency follows the established pattern of creating a
session, yielding it to the request, and closing it afterward.

Conceptually:

``` python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

FastAPI can then provide the session through dependency injection.

### ORM responsibilities

The SQLAlchemy layer is responsible for:

-   Defining database-backed models.
-   Mapping Python attributes to database columns.
-   Querying database records.
-   Creating and updating persisted records.
-   Managing SQLAlchemy sessions.

The ORM layer should not contain browser presentation logic.

------------------------------------------------------------------------

# 9. Pydantic Schemas and Data Validation

Pydantic is used for request and response data validation.

Schemas form an explicit API contract between the client and backend.

For authentication, established request structures include:

### Registration

``` json
{
  "name": "string",
  "email": "email",
  "password": "string"
}
```

### Login

``` json
{
  "email": "email",
  "password": "string"
}
```

The registration validation established in the project includes:

-   Name input.
-   Valid email syntax.
-   Password minimum length of 8 characters.
-   Password maximum length of 72 characters.

`EmailStr` is used for email-format validation.

Email-format validation does **not** prove that a mailbox or domain
actually exists. Real email verification is not currently implemented.

Schemas must not contain database persistence logic.

------------------------------------------------------------------------

# 10. Database Architecture

## 10.1 Current database

LinuxLabX currently uses **SQLite**.

The established development database URL is:

``` text
sqlite:///./linuxlabx.db
```

SQLite is appropriate for the current development setup because it does
not require a separate database server.

## 10.2 SQLAlchemy database foundation

The established database foundation includes:

-   SQLAlchemy engine.
-   SQLAlchemy session factory (`SessionLocal`).
-   Declarative ORM base (`Base`).
-   FastAPI database dependency (`get_db()`).
-   SQLAlchemy models.
-   Initial table creation through:

``` python
Base.metadata.create_all(bind=engine)
```

`create_all()` creates missing tables but is not a database migration
system.

A migration system such as Alembic has not been established as part of
the current implementation.

------------------------------------------------------------------------

# 11. Current Database Entities

The **implemented and confirmed database entity** at the current
development stage is the user entity.

## `users`

The established user model contains:

  Field             Established responsibility
  ----------------- -------------------------------------------
  `id`              User identifier
  `name`            User name
  `email`           User email; unique and indexed
  `password_hash`   Hashed password
  `role`            User role; default is `student`
  `is_active`       User activation status; default is `True`

The database must never store the user's plaintext password.

### Planned domain entities

The project architecture has discussed additional entities for future
learning and gamification modules, including:

-   Learning paths
-   Topics
-   Lessons
-   Practice questions and attempts
-   Quizzes, questions, and attempts
-   Challenges and attempts
-   Progress
-   XP logs
-   Achievements and user achievements
-   Streaks

These should **not** be considered implemented merely because they are
part of the planned architecture. Their final schema and implementation
remain subject to the actual project code at the time they are added.

------------------------------------------------------------------------

# 12. Template and Static-File Architecture

The application contains separate areas for:

``` text
templates/
static/
```

## `templates`

The templates area is intended for Jinja2-rendered HTML.

Jinja2 allows backend-provided values to be inserted into reusable HTML
templates rather than creating a completely separate hard-coded HTML
file for every piece of learning content.

The established project principle is to favor **reusable, data-driven
templates**.

For example, Linux command learning should not require a separate
implementation architecture for every command such as:

``` text
ls
pwd
mkdir
touch
chmod
stat
```

Instead, reusable templates can render command-specific data.

## `static`

The static area contains frontend assets such as:

``` text
static/
├── css/
├── js/
└── images/
```

These assets support the HTML/Jinja2 frontend.

Vanilla JavaScript belongs here rather than being used as a replacement
for backend services.

------------------------------------------------------------------------

# 13. Frontend-to-Backend Communication

The frontend communicates with FastAPI through HTTP.

The architectural relationship is:

``` text
Browser
   |
   | HTTP request
   v
FastAPI route
   |
   v
Pydantic validation
   |
   v
Service logic
   |
   v
SQLAlchemy
   |
   v
SQLite
```

The response follows the reverse direction:

``` text
SQLite
   |
   v
SQLAlchemy
   |
   v
Service
   |
   v
FastAPI
   |
   v
HTML / API response
   |
   v
Browser
```

The exact endpoint contract must remain explicit and must not be changed
silently.

------------------------------------------------------------------------

# 14. Request / Response Flow

A typical backend request follows this sequence:

1.  Browser sends an HTTP request.
2.  FastAPI receives the request.
3.  The route identifies the operation.
4.  Pydantic validates structured request data where a schema is
    defined.
5.  The service/business-logic layer performs the required application
    logic.
6.  SQLAlchemy is used for database access when persistence is required.
7.  SQLite stores or returns the data.
8.  The service returns the result.
9.  FastAPI creates the HTTP response.
10. The browser receives and displays the result.

The purpose of this flow is to keep responsibilities separated.

------------------------------------------------------------------------

# 15. Authentication Architecture

Authentication is currently implemented using JWT.

The established authentication flow is:

``` mermaid
sequenceDiagram
    participant B as Browser
    participant A as FastAPI Auth Route
    participant DB as SQLite via SQLAlchemy

    B->>A: POST /auth/register
    A->>DB: Check email
    DB-->>A: Existing / not existing
    A->>DB: Store user with password hash
    DB-->>A: Created user
    A-->>B: 201 Created

    B->>A: POST /auth/login
    A->>DB: Find user by email
    DB-->>A: User record
    A->>A: Verify password
    A->>A: Create JWT
    A-->>B: access_token + token_type
```

## Registration

The current registration flow:

1.  Validate request data.
2.  Check whether the email already exists.
3.  Hash the password.
4.  Create the user.
5.  Persist the user through SQLAlchemy.
6.  Return a successful response.

Duplicate email registration returns:

``` text
409 Conflict
```

Invalid request validation returns FastAPI/Pydantic validation errors.

## Login

The current login flow:

1.  Receive email and password.
2.  Find the user by email.
3.  Verify the supplied password against the stored password hash.
4.  Generate a JWT.
5.  Return:

``` json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

Invalid credentials return:

``` text
401 Unauthorized
```

The invalid-login response uses a generic message:

``` text
Invalid email or password
```

This avoids revealing whether a particular email address exists.

------------------------------------------------------------------------

# 16. JWT Architecture

The established JWT implementation uses:

-   JWT authentication.
-   `HS256` signing.
-   A configurable secret.
-   An expiration period of 60 minutes.
-   `sub` containing the user ID.
-   `role` in the token payload.
-   `exp` for expiration.

Secrets are configuration values and must not be committed to source
control.

JWT is currently used as the authentication mechanism; the architecture
does not introduce a separate authentication provider.

------------------------------------------------------------------------

# 17. Important Current Data Flows

## 17.1 User registration

``` text
Registration form
      ↓
FastAPI /auth/register
      ↓
Pydantic validation
      ↓
Duplicate-email check
      ↓
Password hashing
      ↓
SQLAlchemy User model
      ↓
SQLite users table
      ↓
HTTP response
```

## 17.2 User login

``` text
Login form
      ↓
FastAPI /auth/login
      ↓
Pydantic validation
      ↓
User lookup
      ↓
Password verification
      ↓
JWT creation
      ↓
Access token response
```

## 17.3 Future learning flow

The product-level learning loop has been established as:

``` text
Learn
  ↓
Practice
  ↓
Quiz
  ↓
Challenge
  ↓
Reward
  ↓
Progress
```

The complete implementation of this flow is not yet represented by the
currently confirmed database/API implementation.

------------------------------------------------------------------------

# 18. Folder-by-Folder Responsibility

The established application structure contains the following areas:

``` text
LinuxLabX/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── templates/
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── tests/
├── docs/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── main.py
```

### `app/`

Application package containing the main modular areas.

### `app/api/`

HTTP/API layer.

### `app/api/routes/`

FastAPI route modules.

### `app/core/`

Core application/configuration/security-related shared infrastructure.

The exact current contents of this directory should be determined from
the source tree rather than assumed.

### `app/models/`

SQLAlchemy ORM models and database-backed entities.

### `app/schemas/`

Pydantic request/response schemas and validation contracts.

### `app/services/`

Business/application logic.

### `app/templates/`

Jinja2 HTML templates.

### `app/static/`

Frontend assets.

### `app/static/css/`

CSS3 stylesheets.

### `app/static/js/`

Vanilla JavaScript.

### `app/static/images/`

Frontend image assets.

### `tests/`

Location reserved for automated tests.

The current conversation has established the directory as part of the
project structure, but the implemented test suite has not been verified
from source code.

### `docs/`

Project documentation.

### `.env`

Local environment configuration and secrets. It must not be committed.

### `.env.example`

Example configuration structure without real secrets.

### `requirements.txt`

Python dependency list generated from the project environment.

### `main.py`

Application entry point for the FastAPI application.

------------------------------------------------------------------------

# 19. Layer Dependency Rules

The intended dependency direction is:

``` text
Presentation / Browser
        ↓
API Routes
        ↓
Pydantic Schemas
        ↓
Services
        ↓
SQLAlchemy Models / Data Access
        ↓
SQLite
```

### API → Schemas

Routes use schemas to validate structured request/response data.

### API → Services

Routes delegate application behavior to services instead of implementing
large business rules inline.

### Services → Models / Database

Services coordinate persistence through SQLAlchemy.

### Models → SQLite

SQLAlchemy maps model operations to the SQLite database.

### Frontend → API

The browser communicates with backend endpoints through HTTP.

### Frontend ↛ Database

Frontend code must never access SQLite directly.

------------------------------------------------------------------------

# 20. Layer Responsibilities and Restrictions

  -----------------------------------------------------------------------
  Layer                   Allowed                 Must not become
                          responsibilities        responsible for
  ----------------------- ----------------------- -----------------------
  Browser / HTML          UI structure and        Database access
                          presentation            

  CSS3                    Visual styling and      Business rules
                          responsive presentation 

  Vanilla JS              Client-side interaction Core backend business
                                                  logic

  Jinja2 templates        Server-rendered HTML    Database transactions
                          presentation            

  FastAPI routes          HTTP handling and       Large business rules
                          orchestration           

  Pydantic                Validation and API data Database persistence
                          contracts               

  Services                Business/application    Browser presentation
                          rules                   

  SQLAlchemy models/data  ORM and persistence     UI behavior
  access                                          

  SQLite                  Persistent development  Application business
                          data                    rules
  -----------------------------------------------------------------------

This separation is an architectural invariant.

------------------------------------------------------------------------

# 21. Current API Structure

The currently established API surface is limited to the endpoints that
have actually been implemented.

## Root

``` text
GET /
```

Used for the application's root/welcome/status response.

## Health

``` text
GET /health
```

Used as the application health endpoint.

## Registration

``` text
POST /auth/register
```

Request:

``` json
{
  "name": "string",
  "email": "email",
  "password": "string"
}
```

Established outcomes include:

-   `201 Created` for successful registration.
-   `409 Conflict` for an already registered email.
-   `422` for invalid request data.

## Login

``` text
POST /auth/login
```

Request:

``` json
{
  "email": "email",
  "password": "string"
}
```

Successful response:

``` json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

Invalid credentials return:

``` text
401 Unauthorized
```

### Important API rule

Only implemented endpoints belong in the current API contract.

Planned endpoints for learning paths, lessons, practice, quizzes,
challenges, XP, achievements, progress, leaderboard, or administration
must not be documented as current endpoints until they are actually
implemented.

------------------------------------------------------------------------

# 22. Error-Handling Approach

The currently verified API behavior includes standard HTTP error
responses for authentication operations.

### Validation errors

Pydantic/FastAPI validation handles invalid structured input.

Example:

-   Invalid email format.
-   Password below the minimum length.
-   Password above the maximum supported length.

### Duplicate registration

``` text
409 Conflict
```

### Invalid login

``` text
401 Unauthorized
```

with a generic invalid-credentials message.

### General principle

Errors should be represented through appropriate HTTP responses rather
than exposing internal implementation details.

The project should not expose:

-   Password hashes.
-   Secrets.
-   Internal authentication details.
-   Raw database internals to the client.

A complete centralized exception-handling architecture has not been
established and should not be assumed.

------------------------------------------------------------------------

# 23. Security Architecture

The security-related architecture currently includes:

## Password hashing

Passwords are not stored as plaintext.

The application stores a `password_hash`.

The project uses Passlib/bcrypt-compatible password hashing as part of
authentication.

A bcrypt compatibility issue was encountered during development and
resolved by using a compatible bcrypt version with the installed Passlib
version.

## JWT authentication

JWT is used for authentication after successful login.

## Secret configuration

JWT secrets are configuration values and should remain outside source
control.

## Input validation

Pydantic validates structured authentication inputs.

## Generic login errors

Invalid login attempts return a generic message rather than revealing
whether an email exists.

## Role field

Users have a `role` field with `student` as the default role.

A complete role/permission matrix has not yet been established as an
implemented authorization system.

------------------------------------------------------------------------

# 24. Testing Architecture

A `tests/` directory is part of the established project structure.

However, the current project source files were not available as a
readable source tree in the provided attachments for this architecture
reconciliation. Therefore, this document does **not** claim a specific
implemented test framework, test module list, coverage level, or CI test
pipeline.

The authentication implementation has been manually tested during
development, including:

-   Successful registration.
-   Duplicate email rejection.
-   Invalid email-format rejection.
-   Short-password rejection.
-   Successful login.
-   Invalid login handling.
-   JWT response generation.

The automated testing architecture should be documented more precisely
once the actual `tests/` source tree is available.

------------------------------------------------------------------------

# 25. Deployment Architecture

The current development stack includes Uvicorn as the ASGI server.

The application is currently structured as a development-oriented
FastAPI + SQLite application.

A production deployment architecture has **not** been established as
implemented.

The synopsis identifies the following technologies as planned future
production technologies:

-   PostgreSQL
-   Docker
-   WebSockets
-   Nginx

Therefore, these are not current deployment components.

No production cloud/VPS architecture, reverse-proxy configuration,
container deployment, or CI/CD deployment pipeline should be treated as
implemented without corresponding source/configuration.

------------------------------------------------------------------------

# 26. Current Limitations

The following limitations are currently established:

1.  SQLite is the current development database.
2.  The current implementation is still being built incrementally.
3.  Authentication currently covers registration and login; a complete
    protected-resource/current-user authorization architecture is not
    yet established.
4.  Full learning, practice, quiz, challenge, gamification, progress,
    leaderboard, and admin implementations are not all confirmed as
    implemented in the current source state.
5.  Real Linux command execution is not part of V1.
6.  A browser-based Linux terminal is future scope.
7.  Email verification is not implemented.
8.  Email syntax validation does not verify real mailbox/domain
    existence.
9.  A migration system such as Alembic is not currently established.
10. A complete automated testing suite has not been verified from the
    available source tree.
11. A production deployment architecture has not been established.

------------------------------------------------------------------------

# 27. Planned Architecture Changes

The following are planned or future architecture directions, not current
implementation.

## 27.1 Production database

The project documentation identifies PostgreSQL as a future production
database.

Current:

``` text
SQLAlchemy → SQLite
```

Planned:

``` text
SQLAlchemy → PostgreSQL
```

The database replacement must be an explicit project decision. SQLite
must not be silently replaced.

## 27.2 Interactive Linux terminal

A future version may provide a browser-based Linux terminal.

This is expected to require architecture beyond the current
request/response learning flow and may use:

-   Docker
-   WebSockets
-   isolated Linux environments

These components are future scope and are not current V1 architecture.

## 27.3 Guided Linux labs

Future guided labs may expand the learning model beyond the current
challenge-oriented approach.

## 27.4 AI learning assistant

An AI-based learning assistant is future scope.

No AI service, provider, API, or architecture is currently part of the
implementation.

## 27.5 Personalized recommendations and analytics

Personalized learning recommendations and performance analytics are
future scope.

Their data model and processing architecture are not currently
implemented.

## 27.6 DevOps learning modules

Future learning areas may include:

-   Git
-   Docker
-   Shell scripting
-   CI/CD
-   Networking
-   Kubernetes
-   Cloud
-   Infrastructure as Code

These are future educational modules, not current backend components.

## 27.7 Production web infrastructure

Nginx and containerized deployment are identified as future
technologies.

They must not be represented as current infrastructure.

------------------------------------------------------------------------

# 28. Architecture Evolution Principle

Future features should extend the existing modular architecture rather
than bypass it.

For example, a future learning module should continue to follow the
established separation:

``` text
Route
  ↓
Schema
  ↓
Service
  ↓
SQLAlchemy Model / Data Access
  ↓
Database
```

Likewise, new browser functionality should remain:

``` text
HTML / Jinja2
      +
CSS3
      +
Vanilla JavaScript
      ↓
FastAPI
```

A future feature must not introduce a new frontend framework or move
core business logic into browser code without explicit architectural
approval.

------------------------------------------------------------------------

# 29. Architecture Invariants

Future AI assistants and developers must preserve the following rules:

1.  **FastAPI remains the backend framework.**
2.  **SQLAlchemy remains the ORM/data-access technology.**
3.  **SQLite remains the current database unless a database migration is
    explicitly approved.**
4.  **Vanilla JavaScript remains the frontend scripting technology.**
5.  **Do not introduce React, Vue, Angular, or another frontend
    framework without explicit approval.**
6.  **Do not move backend business logic into frontend JavaScript.**
7.  **Do not allow frontend code to access the database directly.**
8.  **Keep API contracts explicit.**
9.  **Do not silently change existing API contracts.**
10. **Do not invent endpoints.**
11. **Do not invent database tables and document them as implemented.**
12. **Routes should remain thin.**
13. **Business logic belongs in services.**
14. **Pydantic is used for structured API validation/contracts.**
15. **SQLAlchemy is used for database persistence.**
16. **Passwords must never be stored or returned as plaintext.**
17. **Secrets must not be committed to source control.**
18. **JWT authentication remains part of the established authentication
    architecture.**
19. **Jinja2 remains the server-side HTML template technology.**
20. **Learning content should favor reusable/data-driven templates
    rather than one hard-coded page per Linux command.**
21. **Future architecture must distinguish implemented components from
    planned components.**
22. **Do not add dependencies or technologies without a concrete project
    need and explicit approval.**
23. **Do not silently replace the established stack.**
24. **Do not delete or reset existing architecture/code without
    approval.**
25. **When the actual source code conflicts with an old planning
    document, the implemented source code is the authority for current
    architecture.**

------------------------------------------------------------------------

# 30. Current vs Planned


## Current

  Area                           Current status
  ------------------------------ ----------------------------------
  Language                       Python
  Backend                        FastAPI
  ORM                            SQLAlchemy
  Validation                     Pydantic
  Database                       SQLite
  Frontend                       HTML + CSS3 + Vanilla JavaScript
  Templates                      Jinja2
  Authentication                 JWT
  API server                     Uvicorn
  Application style              Modular monolith
  Database session               SQLAlchemy session dependency
  User registration              Implemented
  User login                     Implemented
  Password hashing               Implemented
  Duplicate email handling       Implemented
  JWT creation                   Implemented
  Root endpoint                  Implemented
  Health endpoint                Implemented
  User ORM entity                Implemented
  Production PostgreSQL          Not implemented
  Browser Linux terminal         Not implemented
  Real Linux command execution   Not implemented in V1
  Docker execution environment   Not implemented
  WebSockets                     Not implemented
  Nginx                          Not implemented
  AI assistant                   Not implemented


## Planned / Future

The following are planned or future architectural areas:

-   Learning-path/content modules beyond the currently implemented
    authentication foundation.
-   Practice system.
-   Quiz system.
-   Challenge system.
-   XP and level system.
-   Achievement system.
-   Progress tracking.
-   Global leaderboard.
-   Admin/content-management functionality.
-   Interactive browser-based Linux terminal.
-   Guided Linux labs.
-   Docker-based isolated Linux environment.
-   WebSocket-based terminal communication.
-   AI learning assistant.
-   Personalized recommendations.
-   Analytics.
-   DevOps learning modules.
-   PostgreSQL production database.
-   Nginx production web server.
-   Containerized deployment.
-   Additional production infrastructure.

These items must only move from **Planned** to **Current** after
implementation is verified.

------------------------------------------------------------------------

# 31. Known Technical Debt

The following technical debt is currently known from the established
development history:

1.  **Database migrations are not yet established.**\
    The current database foundation uses
    `Base.metadata.create_all(...)`. This is sufficient for the current
    development stage but is not a full migration/versioning system.

2.  **Authentication is not yet a complete protected-resource system.**\
    Registration and login are implemented, but the full
    current-user/protected-route authorization architecture has not yet
    been completed.

3.  **Automated test coverage is not yet fully established.**\
    Authentication has been manually verified, but a complete automated
    testing architecture has not been confirmed from the available
    source tree.

4.  **Production deployment architecture is not yet implemented.**\
    PostgreSQL, Docker, WebSockets, and Nginx remain future
    architecture.

5.  **Email verification is not implemented.**\
    Current email validation checks syntax rather than verifying
    mailbox/domain ownership.

No additional technical debt is listed here unless it has been
explicitly established during development.

------------------------------------------------------------------------

# 32. Source-of-Truth Rule for Architecture

LinuxLabX architecture should be maintained using the following
priority:

``` text
Actual implemented source code
        ↓
Confirmed project decisions
        ↓
Current project specification / architecture documentation
        ↓
Earlier planning documents
        ↓
General assumptions
```

If an older document says that a component exists but the actual source
code does not implement it, that component must be documented as
**planned**, not current.

If a future AI assistant cannot verify whether a component exists, it
must not claim that component is implemented.

------------------------------------------------------------------------

# 33. Final Architecture Summary

LinuxLabX currently follows a straightforward layered web-application
architecture:

``` text
HTML / CSS3 / Vanilla JavaScript
              |
              v
          FastAPI
              |
              v
          Pydantic
              |
              v
           Services
              |
              v
        SQLAlchemy ORM
              |
              v
           SQLite
```

The architecture is intentionally simple enough for incremental
development while keeping clear boundaries between presentation, HTTP
handling, validation, business logic, persistence, and data storage.

The current implementation is centered on the authentication foundation
and SQLite-backed user management. The broader learning and gamification
architecture is established as project scope and planned modular
expansion, but must only be described as implemented after the
corresponding source code exists.

Future development must preserve the current stack, explicit API
contracts, layered responsibilities, reusable templates, and separation
between frontend presentation and backend business/data logic.
