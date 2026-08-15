# GridGuard Safety OS

A secure, multi-tenant safety and compliance platform for renewable-energy construction contractors.

GridGuard helps field teams document safety work, identify hazards, assign corrective actions, monitor compliance, and generate audit-ready project records.

## Project Status

GridGuard is under active development.

The initial release is being built as a progressive prototype. Early versions will validate the interface and primary safety workflow before database persistence, authentication, multi-tenancy, reporting, and production infrastructure are introduced.

## The Problem

Small and midsize renewable-energy contractors often manage safety documentation through a mixture of:

* Paper forms
* Spreadsheets
* Email
* Shared drives
* Messaging applications
* Disconnected client systems

This makes it difficult to determine:

* Which hazards remain unresolved
* Who owns each corrective action
* Which work is overdue
* Whether required inspections were completed
* Whether employee training remains current
* What changed during an incident or investigation
* Whether project records are ready for an audit

## The Solution

GridGuard provides one field-friendly system for managing safety and compliance across organizations and project sites.

Workers and supervisors can submit safety information from a phone or tablet. Safety managers can review project risk, assign corrective work, track deadlines, preserve evidence, and generate client-ready reports.

## Initial User Workflow

The first complete GridGuard workflow will allow a supervisor to:

1. Create a project
2. Perform a project inspection
3. Record an unsafe condition
4. Assign a corrective action
5. Set a priority and due date
6. Upload resolution evidence
7. Mark the action complete
8. Verify the completed work
9. Review the complete activity history
10. Include the result in a monthly report

## Planned Features

### Organizations

* Create an organization
* Invite organization members
* Manage user roles
* Isolate data between organizations
* Configure organization settings

### Projects

* Create renewable-energy project sites
* Assign project members
* Track project status
* Generate project QR codes
* Archive completed projects

### Field Documentation

* Safety observations
* Near-miss reports
* Incident reports
* Toolbox talks
* JSA and JHA documentation
* Site inspections
* Worker acknowledgements
* Photographic evidence

### Corrective Actions

* Assign actions to team members
* Set priority and severity
* Set due dates
* Track open and overdue actions
* Attach resolution evidence
* Verify completed work
* Preserve action history

### Training and Compliance

* Track employee training
* Record certifications
* Monitor expiration dates
* Configure role requirements
* Identify missing or expired qualifications

### Reporting

* Project safety summaries
* Monthly safety reports
* Corrective-action reports
* Training-compliance reports
* Inspection histories
* Incident documentation packages
* CSV and PDF exports

### Audit History

GridGuard will record important activity, including:

* Account and membership changes
* Permission changes
* Project updates
* Inspection submissions
* Corrective-action assignments
* Status transitions
* Verification and closure
* Report generation

## Roles

| Role                       | Primary access                                                           |
| -------------------------- | ------------------------------------------------------------------------ |
| Organization administrator | Organization settings, members, permissions, and all projects            |
| Safety manager             | Safety records, inspections, corrective actions, training, and reporting |
| Supervisor                 | Assigned projects, inspections, observations, and corrective actions     |
| Worker                     | Field submissions, acknowledgements, and assigned actions                |
| Client viewer              | Approved read-only project records and reports                           |

The client-viewer role is planned for a later release.

## Technology Stack

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic

### Data and Infrastructure

* PostgreSQL
* Docker
* Docker Compose
* Amazon EC2
* Amazon RDS
* Amazon S3

### Testing and Quality

* Pytest
* Vitest
* React Testing Library
* Playwright
* Ruff
* ESLint
* GitHub Actions

## Architecture

```text
┌───────────────────────────────────┐
│ Next.js Web Application          │
│                                   │
│ Dashboard, field forms, reports, │
│ administration, responsive UI    │
└────────────────┬──────────────────┘
                 │ HTTPS / JSON
                 ▼
┌───────────────────────────────────┐
│ FastAPI Application              │
│                                   │
│ Authentication, authorization,   │
│ validation, business rules       │
└───────────┬───────────────┬───────┘
            │               │
            ▼               ▼
┌────────────────────┐  ┌────────────────────┐
│ PostgreSQL         │  │ Amazon S3          │
│                    │  │                    │
│ Accounts, projects,│  │ Photos, evidence,  │
│ forms, actions,    │  │ attachments, and   │
│ training, audits   │  │ generated reports  │
└────────────────────┘  └────────────────────┘
```

## Repository Structure

```text
gridguard/
├── apps/
│   ├── web/                 # Next.js frontend
│   └── api/                 # FastAPI backend
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   ├── product-requirements.md
│   ├── security.md
│   └── incident-response.md
├── infrastructure/
├── compose.yaml
├── .env.example
├── .gitignore
└── README.md
```

Some directories will be added as the application grows.

## Development Principles

GridGuard is being built around several principles:

* Ship narrow, complete workflows
* Keep tenant-owned data isolated
* Deny access by default
* Enforce permissions in the API
* Validate all external input
* Keep secrets outside source control
* Record security-sensitive activity
* Test important business rules
* Preserve small, understandable Git commits
* Prefer clear code over clever code

## Security Goals

The production application will include:

* Modern password hashing
* Secure HTTP-only sessions
* Role-based access control
* Organization-level data isolation
* CSRF protection
* Validated file uploads
* Rate limiting
* Audit logging
* Dependency scanning
* Container scanning
* Encrypted production traffic
* Database backups
* Incident-response documentation

## Local Development

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

The frontend runs at:

```text
http://localhost:3000
```

### Backend

```bash
cd apps/api
uv sync
uv run fastapi dev app/main.py
```

The API runs at:

```text
http://localhost:8000
```

Interactive API documentation is available at:

```text
http://localhost:8000/docs
```

### Backend Tests

```bash
cd apps/api
uv run pytest
uv run ruff check .
```

## Roadmap

### Milestone 1: Foundation

* [x] Create the Next.js application
* [x] Create the FastAPI application
* [x] Connect the frontend to the API
* [x] Add automated health checks
* [x] Add PostgreSQL through Docker Compose
* [x] Add continuous integration

### Milestone 2: Identity and Tenancy

* [x] Add user accounts
* [x] Add secure sessions
* [x] Add organizations
* [x] Add memberships
* [x] Add invitations
* [x] Add role-based authorization
* [x] Test tenant isolation

### Milestone 3: Project Safety Workflow

* [x] Add projects
* [ ] Add inspections
* [ ] Add safety observations
* [ ] Add corrective actions
* [ ] Add evidence attachments
* [ ] Add audit events

### Milestone 4: Compliance and Reporting

* [ ] Add toolbox talks
* [ ] Add JSA and JHA templates
* [ ] Add training records
* [ ] Add certification expiration tracking
* [ ] Add dashboard analytics
* [ ] Add monthly reports
* [ ] Add data exports

### Milestone 5: Production

* [ ] Add end-to-end tests
* [ ] Add security scanning
* [ ] Add production containers
* [ ] Deploy to AWS
* [ ] Add monitoring
* [ ] Add backups
* [ ] Publish an incident-response runbook

## Portfolio Goals

GridGuard is designed to demonstrate:

* Full-stack TypeScript and Python development
* Product and domain modeling
* Relational database design
* REST API design
* Authentication and authorization
* Multi-tenant SaaS architecture
* Automated testing
* Responsive interface design
* Docker-based development
* CI/CD
* Cloud deployment
* Security-conscious engineering
* Technical documentation
* Incremental development through semantic Git history

## Author

Built by David Spaulding as a production-oriented software engineering and portfolio project.
