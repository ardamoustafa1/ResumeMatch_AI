<div align="center">
  <img src="https://raw.githubusercontent.com/ardamoustafa1/ResumeMatch_AI/main/frontend/src/app/favicon.ico" alt="ResumeMatch AI Logo" width="120" />
  <h1>ResumeMatch AI</h1>
  <p>The Private, Local-First Career Copilot for Top Performers.</p>

  [![CI](https://github.com/ardamoustafa1/ResumeMatch_AI/actions/workflows/ci.yml/badge.svg)](https://github.com/ardamoustafa1/ResumeMatch_AI/actions/workflows/ci.yml)
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

  <p>
    <a href="#features">Features</a> •
    <a href="#quick-start">5-Minute Quick Start</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#roadmap">Roadmap</a>
  </p>
</div>

---

## What is ResumeMatch AI?

ResumeMatch AI is not a generic ChatGPT wrapper. It is a highly engineered, privacy-obsessed system designed to ingest your professional CV alongside target job descriptions, calculate a deterministic mathematical match score, identify missing technical skills, and draft hyper-personalized LinkedIn outreach messages.

**Privacy-First By Default**: Your data is locally processed until AI analysis. We attempt to mask common PII patterns (like emails and phone numbers) before sending data to cloud AI providers (e.g. Groq). By default, uploaded data is completely purged after 30 days.

## Features

- **LLM-Extracted Skill Ratio**: Calculate exact match percentages based on extracted entities, rather than relying on LLM hallucinations for the final number.
- **Actionable Gap Analysis**: Highlights exact keywords and tools missing from your CV that the ATS is looking for.
- **Outreach Draft Generation**: Automatically writes initial connection notes and 7-day follow-ups for hiring managers.
- **Chrome Extension Integration**: Generates API keys to securely analyze job postings directly from your LinkedIn tab.
- **Privacy by Design**: Scoped API keys, hashed database tokens, robust CSPs, and HttpOnly cookies.

## 5-Minute Quick Start

Zero friction onboarding. Get the entire stack running locally in under 5 minutes.

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Bootstrapping

1. **Clone the repository**
   ```bash
   git clone https://github.com/ardamoustafa1/ResumeMatch_AI.git resumematch-ai
   cd resumematch-ai
   ```

2. **Set up Environment Variables**
   ```bash
   cp .env.example .env
   # Add your preferred LLM API key (e.g., Groq, OpenAI) to the .env file.
   ```

3. **Spin up the stack**
   ```bash
   docker compose up --build -d
   ```

4. **Access the application**
   - Frontend Dashboard: [http://localhost:3000](http://localhost:3000)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Production Readiness

Before deploying to production, it is highly recommended to run the full suite of security, load, and integration tests to ensure your environment is hardened:

```bash
# Run Security SAST Scans
pip install bandit pip-audit
bandit -r backend -c backend/pyproject.toml
pip-audit -r backend/requirements.txt

# Run Playwright Accessibility (A11y) & E2E Tests
cd frontend
npm run test:e2e

# Run Locust Load Tests
cd tests
locust -f load_test.py --headless -u 10 -r 2 --run-time 5s --host=http://localhost:8000
```

## Architecture

We use a modern, highly scalable microservices architecture:

- **Frontend**: Next.js 16 (App Router), React 19, TailwindCSS, Zustand.
- **Backend**: FastAPI, AsyncPG, Celery, Redis.
- **Database**: PostgreSQL with Alembic migrations.
- **AI/Extraction**: PyMuPDF, Tesseract OCR, LangChain integrations.

## Roadmap (The 100k Star Journey)

We are building the definitive open-source career copilot. Here is our roadmap:

- [x] **Milestone 1**: Core semantic matching and outreach generation.
- [x] **Milestone 2**: Secure, local-first Docker architecture with Chrome Extension support.
- [ ] **Milestone 3**: Export capabilities (PDF/Docx) and editable analysis drafts.
- [ ] **Milestone 4**: Automated ATS formatting optimizations.
- [ ] **Milestone 5**: Hosted one-click deployment templates (Vercel/Railway).

## Contributing

We welcome contributions from the community! Please read our [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Security

If you discover a security vulnerability, please review our [SECURITY.md](./SECURITY.md) and report it privately.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
