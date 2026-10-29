# LinuxLabX — Project Specification

**Project:** LinuxLabX  
**Document:** `PROJECT_SPEC.md`  
**Status:** Living project specification  
**Scope basis:** Confirmed project requirements, implementation decisions, and the current implementation established in the project conversation and the provided LinuxLabX synopsis.

---

## 1. Project Name

**LinuxLabX**

Working project title from the approved synopsis:

> **LinuxLabX: An Interactive Linux Learning Platform with Gamification and Practical Command-Based Challenges**

---

## 2. Project Purpose and Problem Statement

### Purpose

LinuxLabX is a web-based interactive Linux learning platform designed to make Linux learning more practical, engaging, and beginner-friendly.

The project combines structured Linux learning with practical command-based activities and gamification. The intended learning loop is:

**Learn → Practice → Quiz → Challenge → Reward → Progress**

### Problem Statement

The project is intended to address difficulties faced by beginners and students while learning Linux, including:

- Heavy dependence on theoretical or text/video-based learning.
- Limited opportunities for practical command-based experience.
- Difficulty tracking learning progress.
- Repetitive traditional learning experiences that can reduce motivation.
- Difficulty for beginners who do not want to install or configure Linux locally just to start learning.

LinuxLabX is intended to bridge the gap between theoretical Linux knowledge and practical application through structured learning, practice, challenges, feedback, and gamification.

---

## 3. Project Goals

Confirmed goals include:

1. Provide an interactive platform for learning Linux.
2. Improve practical understanding of Linux commands and concepts.
3. Make Linux learning simple and beginner-friendly.
4. Use gamification such as XP, achievements, streak/progress concepts, and leaderboards to support engagement.
5. Allow users to track learning progress.
6. Help learners develop practical Linux skills useful in real-world IT and DevOps environments.
7. Keep the architecture modular enough for future expansion.

---

## 4. Target Users

Confirmed target users:

- Linux beginners.
- Students, including BCA/MCA/CS/IT learners.
- Learners preparing for Linux-related IT/DevOps skills.
- Users who want structured practical Linux learning without initially setting up a local Linux environment.

More specific demographic segmentation is **TBD**.

---

## 5. Core Features

The current approved V1 scope contains these 12 major features:

1. User Registration & Login
2. User Dashboard
3. Learning Path
4. Learn Module
5. Practice Mode
6. Quiz System
7. Challenge System
8. XP & Level System
9. Achievement System
10. Learning Progress Tracking
11. Global Leaderboard
12. Admin Panel

The synopsis also summarizes the current scope using broader feature labels such as authentication, command challenges, XP, achievements, progress tracking, leaderboard, and responsive UI. The 12-feature list above is the more detailed current V1 breakdown established during development.

---

## 6. Functional Requirements

### 6.1 User Registration and Login

The system shall:

- Allow a user to register with name, email, and password.
- Validate registration input.
- Reject malformed email input.
- Reject passwords below the defined minimum length.
- Prevent duplicate email registration.
- Hash passwords before storing them.
- Provide login using email and password.
- Verify the submitted password against the stored password hash.
- Generate a JWT access token after successful authentication.
- Return an authentication error for invalid credentials.
- Use JWT for protected-resource authentication.

### 6.2 User Dashboard

The dashboard is planned to expose relevant learner information such as:

- XP.
- Level.
- Streak.
- Rank.
- Completed activities.
- Learning progress.
- Continue-learning information.

Exact dashboard layout and exact metrics are **TBD until the dashboard implementation is finalized**.

### 6.3 Learning Path

The learning system is intended to provide:

- Ordered learning paths.
- Topics within paths.
- Lessons within topics.
- Completed/current/locked progression states.
- Structured beginner-oriented learning.

### 6.4 Learn Module

Lessons are intended to contain reusable command/concept information, including where applicable:

- Lesson title.
- Linux command.
- Description.
- Syntax.
- Examples.
- Expected/example output.
- Options.
- Tips.
- Common mistakes.
- Difficulty.
- Display order.

Commands should be represented as data and rendered through reusable templates rather than requiring a separate HTML page for every command.

### 6.5 Practice Mode

Practice functionality is intended to support:

- Practice questions.
- Answer submission.
- Answer validation.
- Correct/incorrect feedback.
- Hints.
- Explanations.
- Attempts.

### 6.6 Quiz System

The quiz system is intended to support:

- Topic-based quizzes.
- Questions such as MCQ, True/False, or scenario-based questions where implemented.
- Scoring.
- Correct-answer explanations.
- Attempts.
- Passing status.

The final exact question types and quiz rules are **TBD until implemented**.

### 6.7 Challenge System

The challenge system is intended to support:

- Linux command-based challenges.
- Challenge descriptions.
- Difficulty.
- Answer submission.
- Answer validation.
- Attempts.
- Hints.
- Explanations.
- XP rewards.
- Progress updates.

V1 challenges validate submitted answers; actual Linux command execution in an isolated environment is future scope.

### 6.8 XP and Level System

The system is intended to:

- Award XP for defined learning activities.
- Maintain XP history.
- Calculate/display user level.
- Support progression through learning activities.

Exact XP values, level thresholds, and XP award rules are **TBD until finalized in implementation**.

### 6.9 Achievement System

The system is intended to:

- Define achievements.
- Check achievement conditions.
- Unlock achievements for users.
- Record achievement unlocks.
- Optionally award XP for achievements.

Exact achievement conditions and catalog are **TBD until implemented**.

### 6.10 Learning Progress Tracking

The system is intended to track:

- Lesson completion.
- Practice completion.
- Quiz completion.
- Challenge completion.
- Topic progress percentage.
- Last activity.

### 6.11 Global Leaderboard

The system is intended to provide a global leaderboard based on defined learner performance/XP data.

The exact ranking rules and tie-breaking behavior are **TBD**.

### 6.12 Admin Panel

The approved V1 scope includes an Admin Panel for content/user management.

Planned administration areas include:

- Users.
- Learning paths.
- Topics.
- Lessons.
- Practice questions.
- Quizzes.
- Challenges.
- Achievements.

Exact admin UI, permissions, audit behavior, and CRUD workflow are **TBD until implemented**.

---

## 7. Non-Functional Requirements

Confirmed or established requirements include:

### Usability

- Beginner-friendly.
- Clear learning progression.
- Clear feedback after interactions.
- Responsive web interface.

### Maintainability

- Modular architecture.
- Reusable templates.
- Avoid unnecessary duplication.
- Business logic separated from HTTP routes.
- Data-driven learning content.

### Security

- Passwords must not be stored in plaintext.
- Passwords are hashed using bcrypt through the current Passlib-based implementation.
- JWT is used for authentication.
- Secrets must not be committed to Git.
- Input validation is required.
- Admin functionality must be protected by authorization.

### API quality

- Appropriate HTTP methods.
- Appropriate HTTP status codes.
- Pydantic validation.
- Clear error responses.
- Thin routes with business logic in services.

### Performance/scalability

The architecture should remain modular and extensible. Detailed performance targets are **TBD**.

---

## 8. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | Backend web framework/API framework |
| SQLAlchemy | ORM/database operations |
| Pydantic | Data validation and API request/response schemas |
| SQLite | Current development database |
| JWT | Authentication/access tokens |
| HTML5 | Web page structure |
| CSS3 | Styling and responsive UI |
| Vanilla JavaScript | Client-side interactivity |
| Jinja2 | Dynamic HTML template rendering |
| Uvicorn | ASGI application server |
| Git | Version control |
| GitHub | Remote repository/project management |
| Visual Studio Code | Development environment |

### Current supporting libraries established during implementation

- `python-jose[cryptography]` for JWT handling.
- `passlib[bcrypt]` for password hashing.
- `email-validator` for Pydantic `EmailStr` validation.
- `python-multipart` was included in the initial dependency setup.
- `pydantic-settings` is used for configuration.

### Dependency compatibility decision

The current password-hashing setup uses:

- Passlib `1.7.4`
- bcrypt `4.0.1`

This was intentionally pinned because the newer bcrypt/Passlib combination produced compatibility problems in the development environment.

---

## 9. Frontend Requirements

The frontend technology is:

- HTML5.
- CSS3.
- Vanilla JavaScript.
- Jinja2 templates.

The UI direction established for LinuxLabX is:

- Professional developer-oriented interface.
- Dark-first visual identity.
- Gameful learning rather than a childish/candy-style game aesthetic.
- Linux/developer/terminal-inspired visual language.
- Responsive design.
- Commands and code should use a monospace typeface.
- Subtle animations rather than excessive animation.

The design direction discussed includes a dark developer palette with Linux-style green plus cyan/blue/purple/gold accents, but exact production colors are **TBD**.

### Reusable templates

The system should use reusable dynamic templates. A separate HTML file should not be created for every individual Linux command.

For example, commands such as `ls`, `pwd`, `mkdir`, `touch`, `chmod`, and `stat` should be represented as lesson data and rendered using a reusable lesson template.

---

## 10. Backend Requirements

The backend uses FastAPI with a layered modular-monolith approach.

Established logical layers:

```text
Browser / Client
      ↓
FastAPI Routes
      ↓
Pydantic Schemas
      ↓
Services
      ↓
SQLAlchemy ORM
      ↓
SQLite
```

### Route responsibility

Routes should:

- Receive HTTP requests.
- Validate/receive schemas.
- Obtain dependencies such as database sessions.
- Call services.
- Convert expected application errors into appropriate HTTP responses.

Routes should not become the primary location for business logic.

### Service responsibility

Services should contain business/application logic such as:

- User creation.
- Duplicate-user checks.
- Password hashing.
- Authentication.
- Future XP/progress/quiz/challenge logic.

### Current database session pattern

The project uses a dependency similar to:

```python
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
```

FastAPI `Depends(get_db)` supplies a database session to routes.

---

## 11. Database Requirements

### Current database

SQLite is the current development database.

Current database URL:

```text
sqlite:///./linuxlabx.db
```

SQLite is being used because it is simple for local development and does not require a separate database server.

A future production database choice of PostgreSQL has been discussed, but it is **not the current database implementation**.

### SQLAlchemy

SQLAlchemy is used as the ORM.

The current database foundation includes:

- SQLAlchemy `engine`.
- `SessionLocal`.
- Declarative `Base`.
- `get_db()` session dependency.
- SQLAlchemy models.
- `Base.metadata.create_all(bind=engine)` for the current initial schema creation approach.

### Current confirmed User model

The `users` table currently contains the established fields:

- `id`
- `name`
- `email`
- `password_hash`
- `role`
- `is_active`

Important constraints:

- `id` is the primary key and auto-incrementing.
- `name` is required.
- `email` is required and unique.
- `email` is indexed.
- `password_hash` is required.
- `role` defaults to `student`.
- `is_active` defaults to `True`.

### Planned data model

The following entities were established as part of the V1 architecture:

- Users.
- Learning paths.
- Topics.
- Lessons.
- Practice questions.
- Practice attempts.
- Quizzes.
- Quiz questions.
- Quiz attempts.
- Challenges.
- Challenge attempts.
- Progress.
- XP logs.
- Achievements.
- User achievements.
- Streaks.

Their exact final SQLAlchemy implementations, relationships, indexes, constraints, and migration strategy are **TBD until implemented**.

---

## 12. API-Related Requirements

The project currently uses FastAPI route-based HTTP APIs.

### Confirmed current routes

#### `GET /`

Returns the LinuxLabX welcome/status response.

#### `GET /health`

Returns a health status response.

#### `POST /auth/register`

Registration endpoint.

Current request fields:

```json
{
  "name": "string",
  "email": "email",
  "password": "string"
}
```

Current behavior:

- Validates request with Pydantic.
- Checks duplicate email.
- Hashes password.
- Creates a user.
- Returns `201 Created` on successful registration.
- Returns `409 Conflict` for duplicate email.
- Returns `422` for Pydantic validation failures.

#### `GET /auth/me`

Protected current-user endpoint. Requires a valid Bearer JWT and returns the authenticated user's safe profile fields (`id`, `name`, `email`, `role`, `is_active`). The password hash is not exposed.

#### `POST /auth/login`

Login endpoint.

Current request fields:

```json
{
  "email": "email",
  "password": "string"
}
```

Current intended behavior:

- Finds user by email.
- Verifies password against stored hash.
- Generates JWT after successful authentication.
- Returns `401 Unauthorized` for invalid credentials.

Current token response shape:

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

### Not yet confirmed/implemented

The protected-route foundation is implemented. `GET /auth/me` is currently implemented and verified. It extracts a Bearer JWT, validates/decodes it, resolves the user from the database, and returns a safe user response without `password_hash`.

---

## 13. Authentication and Authorization Requirements

### Authentication

JWT-based authentication is confirmed.

Registration:

```text
password
   ↓
bcrypt hash
   ↓
password_hash
   ↓
database
```

Login:

```text
email + password
   ↓
find user
   ↓
verify password hash
   ↓
create JWT
```

### JWT

The current design uses:

- JWT.
- HS256 algorithm.
- Configurable secret key.
- Access-token expiry currently configured to 60 minutes.
- JWT payload currently includes:
  - `sub` = user ID.
  - `role` = user role.
  - `exp` = expiry time.

### Authorization

The project has an established `role` field and a `student` default role. Admin functionality is part of V1.

The exact complete authorization matrix and admin permission rules are **TBD** until implemented.

---

## 14. Important Business Rules

Confirmed rules:

1. New users default to the `student` role.
2. Email addresses must be unique.
3. Passwords must not be stored in plaintext.
4. Password input currently has a minimum length of 8 and maximum length of 72 characters at the Pydantic schema level.
5. Email format is validated using Pydantic `EmailStr`.
6. A syntactically valid email address does not mean the domain/mailbox actually exists. Real email verification is not currently implemented.
7. Invalid login credentials return a generic `Invalid email or password` response rather than exposing whether an email exists.
8. SQLite is the current development database.
9. Real Linux command execution is not part of V1.
10. V1 command challenges validate submitted answers rather than execute commands in a real Linux environment.
11. Learning content should be data-driven and rendered through reusable templates.
12. New features outside the approved scope should not be introduced without explicit approval.

---

## 15. UI/UX Requirements

The established UI direction is:

- Professional.
- Developer-oriented.
- Dark-first.
- Linux/terminal inspired.
- Gameful rather than childish.
- Responsive.
- Clear progression.
- Clear feedback.
- Subtle reward animations.

The core interaction philosophy established during design discussions is:

```text
What am I learning?
        ↓
What should I do?
        ↓
Was I correct?
        ↓
Why?
        ↓
What should I do next?
```

The learning experience should communicate progression and provide visible learner feedback.

### Visual inspiration

The project may take conceptual inspiration from modern developer products and learning platforms, but LinuxLabX should not copy another product's exact visual design.

CloudAttack's progression mechanics were considered useful inspiration for learning progression, but its exact Candy-Crush-like visual treatment was explicitly not adopted as the LinuxLabX visual identity.

---

## 16. Project Constraints

1. Current technology stack must remain unchanged unless explicitly approved.
2. Development is being done from a fresh scratch implementation; older implementations are not the source of truth.
3. Current V1 must remain within the approved 12-feature scope.
4. Real Linux command execution is future scope, not V1.
5. Docker-based isolated Linux environments are future scope.
6. The project should not be over-engineered prematurely.
7. New libraries or technologies should not be introduced without a project need and explicit approval.
8. Database/schema changes should eventually use a migration system such as Alembic rather than repeatedly deleting the database; migration adoption is planned but not yet implemented.
9. Secrets must not be committed to Git.
10. `.env` files are excluded from version control.
11. Generated/local SQLite database files are excluded from version control.

---

## 17. Coding Conventions and Rules

Established development rules:

- Use clear, descriptive names.
- Use Python type hints.
- Keep routes thin.
- Put business logic in service modules.
- Use Pydantic schemas for request validation.
- Use SQLAlchemy models for database representation.
- Reuse templates instead of duplicating pages.
- Avoid duplicated business logic.
- Keep code modular and readable.
- Use proper HTTP methods and status codes.
- Validate user input.
- Handle expected errors clearly.
- Keep secrets/configuration outside source code for production use.
- Use descriptive Git commit messages.
- Review AI-generated code instead of blindly accepting it.
- Do not create duplicate models/routes/services for functionality that already exists.
- Follow the established project architecture when adding features.

---

## 18. Things That Must NOT Be Changed Without Explicit Approval

The following should not be changed without explicit approval:

### Technology stack

- FastAPI
- Python
- SQLAlchemy
- Pydantic
- SQLite as the current development database
- JWT authentication
- HTML5
- CSS3
- Vanilla JavaScript
- Jinja2

### Product scope

The current 12-feature V1 scope must not be silently expanded.

### Architecture

The project should continue following the established modular layered structure:

```text
Routes → Schemas → Services → SQLAlchemy → Database
```

### Product positioning

LinuxLabX should remain a professional, beginner-friendly, gameful Linux learning platform rather than becoming a generic game website.

### Execution model

Real Linux command execution is future scope and must not be silently added to V1.

---

## 19. Current Implementation Status

The project is currently in early backend development. The authentication foundation now includes a verified protected current-user endpoint (`GET /auth/me`).

### Completed foundation

- Project created from scratch.
- Python virtual environment created.
- Dependencies installed.
- Git initialized.
- `.gitignore` created.
- GitHub repository configured.
- Initial project folder structure created.
- FastAPI application created.
- Uvicorn development server working.
- Root route working.
- Health route working.
- SQLite database configured.
- SQLAlchemy base/session setup created.
- `User` SQLAlchemy model created.
- User table creation verified.
- Pydantic registration schema created.
- User service created.
- Registration route created.
- Password hashing implemented.
- Duplicate email handling implemented.
- Email format validation implemented.
- Password length validation implemented.
- JWT configuration/token generation implemented.
- Login service and login route implemented.
- Protected JWT authentication dependency implemented.
- `GET /auth/me` protected current-user endpoint implemented and verified.
- Safe `UserResponse` schema implemented so password hashes are not exposed.

### Current registration behavior verified during development

The following were tested successfully:

- Valid user registration.
- Duplicate email rejection.
- Invalid email-format rejection.
- Short password rejection.
- Proper HTTP error responses.

A dependency compatibility issue between Passlib and a newer bcrypt version was encountered and resolved by using bcrypt `4.0.1` with Passlib `1.7.4`.

---

## 20. Completed Features

### Completed at implementation level

**Authentication foundation:**

- Registration endpoint.
- Password hashing.
- Duplicate email handling.
- Registration input validation.
- Login endpoint.
- Password verification.
- JWT generation.
- Protected JWT route handling.
- Current-user (`GET /auth/me`) endpoint.
- Safe authenticated-user response schema.

**Infrastructure:**

- FastAPI app.
- Uvicorn server.
- SQLite.
- SQLAlchemy session/base.
- User model.
- Pydantic schemas.
- Basic service layer.
- Git/GitHub repository.

### Not yet complete as product features

The following approved V1 features have not yet been implemented:

- User Dashboard.
- Learning Path.
- Learn Module.
- Practice Mode.
- Quiz System.
- Challenge System beyond the currently planned architecture.
- XP & Level System.
- Achievement System.
- Learning Progress Tracking.
- Global Leaderboard.
- Admin Panel.

---

## 21. Pending Features

The remaining V1 work includes:

1. Extend the authentication flow as needed (protected-route foundation and `GET /auth/me` are complete).
2. User dashboard.
3. Learning path.
4. Learn module.
5. Practice mode.
6. Quiz system.
7. Challenge system.
8. XP and levels.
9. Achievements.
10. Progress tracking.
11. Leaderboard.
12. Admin panel.
13. Frontend pages/templates and responsive UI.
14. Testing and integration.
15. Final UI/UX polish.
16. Production/release preparation.

Exact implementation order should continue to follow the project's phased development plan unless explicitly changed.

---

## 22.1 Current Development Checkpoint / Next Starting Point

**Last verified completed checkpoint:** JWT authentication is working end-to-end through registration, login, token generation, protected dependency handling, and `GET /auth/me`.

The next development chat should **not restart authentication or rebuild the project foundation**.

### Start from here

1. First inspect the actual current codebase and reconcile it with this document and `ARCHITECTURE.md`.
2. Preserve the existing authentication implementation and do not create duplicate auth models, schemas, services, or routes.
3. Continue with the next approved V1 feature after authentication. The immediate product-development direction is the **User Dashboard**, unless the project owner explicitly changes the order.
4. Before implementing the dashboard, determine the minimum user/progress data actually required from the current codebase rather than inventing database fields.
5. Continue incrementally: design the data model → schema/service/API → test → then frontend/template work.
6. Explain new SQLAlchemy/FastAPI concepts because the project owner is learning while building.
7. Do not update project documentation merely by assumption; update it only after implementation is actually verified.

### Authentication checkpoint

Current verified authentication capabilities:
- Registration
- Password hashing
- Duplicate-email protection
- Input validation
- Login
- Password verification
- JWT generation
- JWT protected dependency
- `GET /auth/me`
- Safe authenticated-user response without password hash

## 22. Known Limitations

1. Current database is SQLite and is intended primarily for development.
2. Actual Linux command execution is not implemented.
3. Email domain/mailbox existence is not verified during registration.
4. Email verification is not implemented.
5. Full authorization/admin protection is not yet implemented.
6. The complete frontend is not yet implemented.
7. Learning, practice, quiz, challenge, gamification, progress, leaderboard, and admin features are not yet complete.
8. Database migrations are not yet implemented.
9. Exact production deployment architecture is not finalized.
10. Exact XP/level/achievement rules are not finalized.

---

## 23. Known Bugs

No confirmed unresolved application bug is currently recorded.

### Resolved development issue

A Passlib/bcrypt compatibility issue caused errors such as:

```text
error reading bcrypt version
AttributeError: module 'bcrypt' has no attribute '__about__'
```

and misleading password-length behavior.

The development environment was corrected by using a compatible bcrypt version (`4.0.1`) with Passlib (`1.7.4`).

---

## 24. Future Requirements Discussed but Not Implemented

The following have been explicitly discussed as future scope and must not be treated as current V1 functionality:

- Interactive browser-based Linux terminal.
- Real Linux command execution.
- Docker-based isolated Linux environment.
- Interactive/guided Linux labs.
- AI learning assistant.
- Personalized learning recommendations.
- Advanced analytics/performance dashboard.
- DevOps learning modules such as Git, Docker, Shell Scripting, CI/CD, Networking, Kubernetes, Cloud, and Infrastructure as Code.
- Real-world DevOps missions.
- PostgreSQL for production.
- WebSockets for real-time terminal communication.
- Nginx for production web serving.
- GitHub Actions/CI.
- Cloud/VPS deployment.
- Classroom management.
- Certificate generation.
- Mobile application.

These are future extensions, not current V1 requirements.

---

## 25. Important Decisions Already Made

### Fresh-scratch development

The project is being developed from scratch. Earlier implementations are not the source of truth.

**Reason:** The project should have a clean, understandable architecture rather than carrying forward previous implementation decisions.

### Modular layered backend

The project uses:

```text
Routes
  ↓
Schemas
  ↓
Services
  ↓
SQLAlchemy
  ↓
Database
```

**Reason:** Keep HTTP handling, validation, business logic, and persistence responsibilities separated.

### SQLite for development

SQLite was selected for the current development phase.

**Reason:** It is simple to run locally without requiring a separate database server.

### Reusable lesson templates

Individual Linux commands should not require individual HTML pages.

**Reason:** Commands and lesson content should be stored as data and rendered through reusable templates, making content expansion and admin management easier.

### Professional gameful UI

The project uses gamification mechanics without copying childish game visuals.

**Reason:** LinuxLabX is intended to feel useful for serious Linux/DevOps learning while still being engaging.

### Real command execution is future scope

V1 challenges validate submitted answers rather than executing commands.

**Reason:** Real execution introduces sandboxing, containerization, security, resource limits, and infrastructure complexity that are intentionally deferred.

### AI-assisted development with human review

AI is being used to help develop the project, but generated code should be understood, reviewed, tested, and kept aligned with this specification.

---

# Source of Truth

Future AI chats working on LinuxLabX should use the following priority order:

1. **Explicitly confirmed decisions in the current project conversation.**
2. **The actual current project code and configuration.**
3. **`PROJECT_SPEC.md`**, when it reflects the current confirmed implementation.
4. Other project documentation such as PRD/FRD/Architecture/Rules/Phases/Design/Memory.
5. The approved project synopsis for the broader academic project description.

If two sources conflict, the conflict must be surfaced rather than silently resolved.

An AI assistant must not convert an idea, suggestion, example, or future-scope item into an implemented requirement.

The actual codebase must be checked before claiming that a feature is implemented.

---

# AI Development Rules

Future AI assistants must follow these rules:

1. **Do not invent requirements.**
2. **Do not invent APIs, database tables, roles, workflows, or technologies.**
3. **Treat this document and the actual codebase as project context, not as permission to expand scope.**
4. **Ask for explicit approval before adding out-of-scope features.**
5. **Do not change the established technology stack without approval.**
6. **Follow the layered architecture: Routes → Schemas → Services → SQLAlchemy → Database.**
7. **Keep routes thin and business logic in services.**
8. **Use Pydantic for API input validation.**
9. **Use SQLAlchemy models for database persistence.**
10. **Never store plaintext passwords.**
11. **Do not expose passwords or password hashes in API responses.**
12. **Keep secrets out of source control.**
13. **Use reusable templates and data-driven content.**
14. **Do not create one page/template per Linux command.**
15. **Do not add real Linux command execution to V1 without explicit approval.**
16. **Do not silently replace SQLite with another database.**
17. **Do not introduce a new dependency unless it is justified and approved/consistent with the project.**
18. **Test each meaningful implementation step before moving forward.**
19. **Explain important new technical concepts when implementing them because the project owner is using AI-assisted/vibe coding and is learning the stack while building.**
20. **When a topic is substantially new or difficult, identify it clearly and recommend targeted learning rather than hiding the complexity.**
21. **Do not claim something is completed unless it has actually been implemented and verified.**
22. **Maintain compatibility with the existing code instead of creating parallel implementations.**
23. **Use clear naming, type hints, modular code, and descriptive commits.**
24. **Do not delete or reset existing project data/code merely to make a new implementation easier without explicit approval.**
25. **When uncertain, mark the item as TBD or ask before deciding.**

---

# Unknown / TBD

The following important items are not fully decided or implemented yet:

- Exact final database schema and relationships for every V1 entity.
- Exact XP values.
- Exact level thresholds.
- Exact achievement catalog and unlock conditions.
- Exact streak rules.
- Exact leaderboard ranking and tie-breaking rules.
- Exact quiz question types and scoring rules.
- Exact challenge validation rules for every challenge type.
- Exact admin permission matrix.
- Exact dashboard layout and metrics.
- Exact frontend page list beyond the high-level pages already discussed.
- Exact production color palette and final UI tokens.
- Exact responsive breakpoints.
- Exact production deployment architecture.
- Exact PostgreSQL migration/deployment plan.
- Exact Alembic migration workflow.
- Exact JWT secret-management/deployment mechanism.
- Exact refresh-token strategy, if any.
- Exact token revocation/logout strategy.
- Exact email verification workflow.
- Exact password-reset workflow.
- Exact rate-limiting strategy.
- Exact automated test coverage targets.
- Exact CI/CD workflow.
- Exact production hosting/cloud provider.
- Exact production security hardening checklist.
- Exact analytics requirements.
- Exact content-authoring/admin workflow.
- Exact future DevOps curriculum structure.

These items must remain **TBD** until explicitly decided or implemented.
