# CivicPulse

CivicPulse is a civic complaint management platform that allows citizens to submit complaints, track complaint status, and view aggregated complaint statistics. The system combines a React frontend, FastAPI backend, PostgreSQL persistence, Redis caching/rate limiting, and an AI-assisted complaint triage layer with deterministic fallbacks.

## 1. Project Overview

CivicPulse is designed around the following workflow:

1. A citizen submits a complaint.
2. The backend validates the request.
3. The complaint is sent through the configurable triage layer.
4. The selected provider determines the complaint category, priority, summary, and confidence.
5. The complaint is stored in PostgreSQL.
6. Redis is used for caching and distributed rate limiting.
7. Citizens can view complaints, track status, and view statistics.

The system is designed so that complaint submission does not depend entirely on the availability of an external AI provider. If the configured LLM provider fails, the deterministic rule-based provider can be used as a fallback.

## 2. Main Features

### Citizen complaint management

* Submit a complaint with complaint text and location.
* Validate complaint input before submission.
* Automatically classify complaints.
* Assign complaint priority.
* Generate a short complaint summary.
* View submitted complaints.
* View individual complaint details.
* Track complaint status.
* View aggregate statistics.

### AI-assisted triage

CivicPulse supports four triage providers:

* LLM provider using Groq.
* Ollama provider for local LLM execution.
* Rule-based provider.
* Simulated provider for deterministic development and CI testing.

The provider is selected through the `TRIAGE_PROVIDER` environment variable.

The triage abstraction is documented in:

* `backend/app/providers/base.py`
* `backend/app/providers/factory.py`
* `backend/app/providers/llm_provider.py`
* `backend/app/providers/ollama_provider.py`
* `backend/app/providers/rule_provider.py`
* `backend/app/providers/simulated_provider.py`

Additional design information is available in `docs/adr/0001-provider-interface.md` and `docs/TRIAGE.md`.

### Reliability and fallback

The LLM provider uses a timeout and retry mechanism. When the LLM cannot successfully produce a valid result, the deterministic `RuleProvider` provides a fallback classification.

The provider that ultimately produced the result is recorded using `triaged_by`.

This allows the system to distinguish normal AI classification from fallback classification.

## 3. Architecture

CivicPulse follows a layered backend architecture.

```text
React / TypeScript Frontend
            |
            v
       FastAPI Routes
            |
            v
        Services
            |
      +-----+------+
      |            |
      v            v
Repositories    Triage Layer
      |            |
      v       +----+----------------+
 PostgreSQL   |    |       |        |
              v    v       v        v
             LLM Ollama  Rules  Simulated
              |
              v
            Groq
```

The backend separates HTTP routing, business services, data access, and external provider integrations.

### Backend layers

* Routes: HTTP API endpoints.
* Services: business logic and state transitions.
* Repositories: database access.
* Providers: complaint triage implementations.
* Cache: Redis-backed caching and rate limiting.
* Database: PostgreSQL.

## 4. Repository Structure

```text
CivicPulse-SCD-project/
│
├── backend/
│   ├── app/
│   │   ├── cache/
│   │   ├── providers/
│   │   ├── repositories/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── alembic/
│   ├── scripts/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.ts
│
├── k8s/
│   ├── base/
│   └── overlays/
│
├── docs/
│   ├── adr/
│   ├── evidence/
│   ├── AI-USAGE.md
│   ├── API-CONTRACT.md
│   ├── ENGINEERING-NOTES.md
│   ├── RUNBOOK.md
│   └── TRIAGE.md
│
├── .github/
│   └── workflows/
│
├── docker-compose.yml
└── README.md
```

## 5. Frontend

The frontend is built with:

* React
* TypeScript
* Vite
* React Router
* Nginx for production serving

Main application pages include:

* `/` - Submit Complaint
* `/dashboard` - Complaint Dashboard
* `/stats` - Statistics

Frontend source code is located under:

```text
frontend/src/
```

### Frontend validation and testing

The frontend provides:

* Input validation.
* Loading states.
* Complaint submission feedback.
* Dashboard filtering and pagination.
* Status handling.
* Statistics display.
* API error handling.

Frontend commands:

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
npm test
npm run test:coverage
npm run build
```

The frontend test suite includes meaningful tests for complaint submission, validation, dashboard behavior, statistics, filtering, and navigation.

## 6. Backend

The backend is implemented using FastAPI and Python.

Main backend technologies include:

* FastAPI
* SQLAlchemy
* PostgreSQL
* Alembic
* Redis
* Pydantic
* Pytest

Backend source code is located under:

```text
backend/app/
```

### API endpoints

The main API contract includes:

```text
POST   /api/complaints
GET    /api/complaints
GET    /api/complaints/{id}
PATCH  /api/complaints/{id}/status
GET    /api/stats
GET    /api/meta/providers
GET    /api/health
```

The detailed API contract is documented in:

```text
docs/API-CONTRACT.md
```

## 7. Database

CivicPulse uses PostgreSQL for persistent complaint data.

Database migration management is handled using Alembic.

Migration files are located in:

```text
backend/alembic/
```

The initial migration is:

```text
backend/alembic/versions/0001_initial.py
```

Database access is separated from route and service logic through the repository layer.

## 8. Redis

Redis is used for application-level caching and rate limiting.

Relevant implementation files include:

```text
backend/app/cache/triage_cache.py
backend/app/cache/rate_limiter.py
```

The triage cache stores results using a SHA-256 content hash and a time-to-live.

Redis also supports distributed rate limiting so that rate-limit state is not dependent on a single backend process.

## 9. AI Triage

The triage layer uses a common provider abstraction.

Available providers:

```text
llm
ollama
rules
simulated
```

Provider selection:

```text
TRIAGE_PROVIDER=llm
```

The LLM provider uses structured output validation before the result is accepted.

The triage result contains information such as:

* Category
* Priority
* Summary
* Confidence

### LLM failure handling

The LLM provider uses a timeout. Timeout failures can be retried, and failed or invalid provider results can fall back to the deterministic rule provider.

This design means that an external AI outage does not necessarily prevent complaint submission.

Detailed triage documentation:

```text
docs/TRIAGE.md
docs/adr/0001-provider-interface.md
docs/adr/0004-pii-and-data-governance.md
```

## 10. Data Governance

The complaint reporter's contact information is kept separate from the data intentionally passed to the triage provider.

The current implementation does not automatically redact PII that a citizen may voluntarily include inside free-form complaint text. This is documented as a known limitation.

The relevant architectural decision is documented in:

```text
docs/adr/0004-pii-and-data-governance.md
```

## 11. Testing

### Backend

Run:

```bash
cd backend
pip install -r requirements.txt
pytest
```

Run coverage:

```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=65
```

The backend test suite covers:

* Complaint routes
* Health endpoints
* Statistics
* Provider behavior
* Prompt-injection handling
* Status transitions
* Triage fallback behavior

### Frontend

Run:

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
npm run test:coverage
npm run build
```

The frontend test suite verifies key user-facing behavior including complaint validation, submission, dashboard behavior, statistics, filtering, and navigation.

## 12. Docker

The project includes containerization for the frontend and backend.

Frontend:

```text
frontend/Dockerfile
frontend/.dockerignore
```

Backend:

```text
backend/Dockerfile
backend/.dockerignore
```

The frontend uses a multi-stage build and serves the generated application using Nginx.

Docker Compose configuration is available at:

```text
docker-compose.yml
```

Start the development stack with:

```bash
docker compose up
```

Stop the stack with:

```bash
docker compose down
```

## 13. Kubernetes

Kubernetes manifests are maintained under:

```text
k8s/
```

The project uses a base configuration and production overlay.

The Kubernetes configuration includes application deployments and supporting infrastructure such as PostgreSQL and Redis.

Typical inspection commands include:

```bash
kubectl get pods -n civicpulse
kubectl get services -n civicpulse
kubectl get deployments -n civicpulse
```

Deployment-specific evidence is stored under:

```text
docs/evidence/
```

Some Kubernetes scaling and networking evidence remains dependent on the final Kubernetes workstream and load-test execution.

## 14. CI/CD

GitHub Actions workflows are stored under:

```text
.github/workflows/
```

Current workflows include:

```text
backend-ci.yml
frontend-ci.yml
cd.yml
```

### Backend CI

Backend CI installs Python dependencies and executes the backend test suite with coverage enforcement.

### Frontend CI

Frontend CI:

1. Installs Node.js dependencies.
2. Runs linting.
3. Runs TypeScript type checking.
4. Runs tests with coverage.
5. Builds the production frontend.

### Continuous Deployment

The CD workflow runs on pushes to the repository's shared `dev` branch and can also be triggered manually.

The workflow tests the application, publishes container images to GitHub Container Registry, and performs the deployment workflow.

Published images use the Git commit SHA as their image tag.

## 15. GitHub Container Registry

CivicPulse container images are published to GitHub Container Registry.

The image naming convention is:

```text
ghcr.io/minah-bot/civicpulse-backend:<commit-sha>
ghcr.io/minah-bot/civicpulse-frontend:<commit-sha>
```

Evidence of published image tags is available under:

```text
docs/evidence/
```

## 16. Engineering Documentation

Additional engineering decisions and operational documentation are available in:

```text
docs/adr/
docs/API-CONTRACT.md
docs/ENGINEERING-NOTES.md
docs/RUNBOOK.md
docs/TRIAGE.md
docs/AI-USAGE.md
```

The ADRs document important architectural decisions including:

* Provider abstraction.
* Frontend architecture.
* Frontend containerization.
* PII and data governance.

## 17. AI Usage

AI tools were used as development assistance for areas including:

* Frontend testing.
* Backend testing and coverage.
* CI troubleshooting.
* ESLint configuration.
* Docker/configuration review.
* Git and GitHub Actions troubleshooting.

Human team members remained responsible for implementation, testing, integration, and final engineering decisions.

See:

```text
docs/AI-USAGE.md
```

## 18. Evidence

Project evidence is stored under:

```text
docs/evidence/
```

Evidence includes screenshots for:

* Backend CI
* Frontend CI
* CD
* Pull requests
* GitHub Container Registry images
* Commit history

## 19. Known Limitations

Some deployment and infrastructure evidence depends on the final Kubernetes workstream.

Known documentation/evidence limitations include:

* HPA load-test measurements and replicas-versus-load evidence require the completed Kubernetes load test.
* VPA recommendation evidence requires the completed Kubernetes configuration and observation.
* Final production networking behavior requires verification against the final Kubernetes manifests.
* Free-form complaint text is not currently automatically PII-redacted before an external LLM provider receives it.
* Triage cache hit-rate measurements should be recorded from an actual repeated-submission test.

These limitations are documented explicitly rather than represented as completed features without evidence.

## 20. Development Workflow

The project uses feature branches for development.

Typical workflow:

```bash
git checkout -b feature/<name>
git add .
git commit -m "feat: description"
git push -u origin feature/<name>
```

Changes are integrated through pull requests and CI validation.

Useful commands:

```bash
git status
git log --oneline -10
git shortlog -sn
git branch -a
```

## 21. Project Documentation Map

| Document                                    | Purpose                                                    |
| ------------------------------------------- | ---------------------------------------------------------- |
| `README.md`                                 | Project overview, architecture, setup, testing, deployment |
| `docs/API-CONTRACT.md`                      | API contract                                               |
| `docs/TRIAGE.md`                            | AI triage design and fallback behavior                     |
| `docs/RUNBOOK.md`                           | Operational and troubleshooting procedures                 |
| `docs/ENGINEERING-NOTES.md`                 | Engineering questions and design reasoning                 |
| `docs/AI-USAGE.md`                          | AI assistance disclosure                                   |
| `docs/adr/0001-provider-interface.md`       | Provider abstraction decision                              |
| `docs/adr/0004-pii-and-data-governance.md`  | PII and external LLM data governance                       |
| `docs/adr/001-frontend-architecture.md`     | Frontend architecture                                      |
| `docs/adr/002-frontend-containerization.md` | Frontend containerization                                  |

## 22. Project Status

CivicPulse contains implemented frontend, backend, persistence, caching, AI triage, testing, containerization, and CI/CD components.

Infrastructure-specific rubric evidence is maintained separately where it requires live Kubernetes measurements or deployment observations.
