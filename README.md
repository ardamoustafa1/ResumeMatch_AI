<div align="center">
  <img src="https://raw.githubusercontent.com/ardamoustafa1/NetworkForge/main/frontend/public/icon.svg" alt="ResumeMatch AI Logo" width="120" />
  <h1>ResumeMatch AI</h1>
  <p>The Private, Local-First Career Copilot for Top Performers.</p>

  [![CI](https://github.com/ardamoustafa1/NetworkForge/actions/workflows/ci.yml/badge.svg)](https://github.com/ardamoustafa1/NetworkForge/actions/workflows/ci.yml)
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

ResumeMatch AI is not a generic ChatGPT wrapper. It is a highly engineered, privacy-obsessed system designed to ingest your professional CV alongside target job descriptions, calculate an exact semantic match score, identify missing technical skills, and draft hyper-personalized LinkedIn outreach messages.

**Your data stays yours.** With our local-first Docker architecture, your PII is never permanently stored on third-party servers.

## Features

- **Deep Semantic Matching**: Calculates a deterministic percentage match between your CV and the role.
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
   git clone https://github.com/ardamoustafa1/NetworkForge.git resumematch-ai
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

## Architecture

We use a modern, highly scalable microservices architecture:

- **Frontend**: Next.js 15 (App Router), React 19, TailwindCSS, Zustand.
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
