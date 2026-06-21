# Contributing to ResumeMatch AI

First off, thank you for considering contributing to ResumeMatch AI! It's people like you that make this tool a powerful, privacy-first career copilot for everyone.

## Getting Started

1. **Fork the Repository**: Start by forking the repository to your GitHub account.
2. **Clone Locally**: Clone your fork to your local machine.
3. **Environment Setup**: Follow the README instructions to spin up the local Docker environment (`docker compose up --build`).

## Development Workflow

1. Create a descriptive branch name (`git checkout -b feat/add-new-model` or `fix/ws-race-condition`).
2. Make your changes in small, logical commits.
3. Ensure all tests pass. If you're adding a new feature, please add corresponding test coverage.
    - Run backend tests: `pytest`
    - Run frontend tests: `cd frontend && npm test`
4. Lint and format your code:
    - Backend: `ruff check backend tests` and `ruff format --check backend tests`
    - Frontend: `npm run lint`

## Pull Request Process

1. Push your branch to your fork.
2. Open a Pull Request against the `main` branch of this repository.
3. Provide a clear and comprehensive description of the changes. Include screenshots or videos if you are making UI changes.
4. Ensure your PR passes all GitHub Actions CI checks (CodeQL, Gitleaks, Pytest, Linting).
5. Address any review comments promptly.

Run the complete local gate with `make qa`. Pull requests that change
authentication, privacy, provider data flow, uploads, or deployment behavior
must update the threat model and relevant tests.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and constructive in all communications.
