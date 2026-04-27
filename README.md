# NetworkForge 🔨

[![Build Passing](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-80%25-green.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)]()
[![Stars](https://img.shields.io/github/stars/yourusername/networkforge.svg?style=social)]()

> **AI copilot that turns your CV into personalized recruiter conversations.**

![demo](docs/demo.gif)

## Why NetworkForge?

*   **Most job applications fail because outreach is generic.** Applying through standard portals puts your resume in a black box. Standing out requires targeted, human connection.
*   **Recruiters get 100+ messages a day; personalization wins.** If you send a generic "Hi, I applied", you get ignored. NetworkForge analyzes your specific CV against their exact Job Description to highlight exactly why you're a match.
*   **This automates the research and writing, not the thinking.** It gives you the perfect 90% draft. You review, tweak, and hit send. 

## Features

| Feature | Status |
| :--- | :---: |
| Match Score (0-100) | ✅ |
| Missing Skills Detection | ✅ |
| Personalized LinkedIn DM | ✅ |
| Follow-up Message (Day 7) | ✅ |
| Connection Request Note | ✅ |
| LinkedIn Headline Rewrite | ✅ |
| About Section Rewrite | ✅ |
| Telegram Notifications | ✅ |
| Real-time WebSocket Progress | ✅ |

## Architecture

Built for scale and speed, entirely asynchronous. If OpenAI goes down, the system automatically fails over to local Ollama.

```text
[User / Client]
       │
       ├─ (1) POST /api/v1/analyze
       │
[FastAPI] ──(2) Save Pending State ──> [PostgreSQL]
       │
       ├─ (3) Enqueue Task ──────────> [Redis (Broker)]
       │                                     │
       ├─ (4) Return Task ID                 v (5) Consume
       │                               [Celery Worker]
       ├─ (6) WS connect <───────────────────┤
                                             ├─ (7) AI Engine (GPT-4o-mini / Llama3)
                                             ├─ (8) Update DB [PostgreSQL]
                                             └─ (9) Notify [Telegram API]
```

## Quick Start 🚀

Get the entire backend running in under 5 minutes.

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/networkforge.git
cd networkforge

# 2. Setup your environment
cp .env.example .env

# 3. Add your OpenAI API key to .env
# OPENAI_API_KEY=sk-...

# 4. Spin up the cluster
make dev
```
*Note: This starts FastAPI, Celery, PostgreSQL, Redis, and Redis-Commander locally.*

## API Usage

**1. Start an Analysis**
```bash
curl -X POST http://localhost:8000/api/v1/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "Experienced Python developer with 5 years in FastAPI, PostgreSQL, and AWS...",
    "jd_text": "Looking for a Senior Backend Engineer proficient in Python, AsyncIO, and Redis...",
    "company": "Stripe",
    "recruiter_name": "Elif Şahin"
  }'
```
*Returns `HTTP 202` with an `analysis_id`.*

**2. Check Progress via WebSocket**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/analysis/<analysis_id>');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

**3. Retrieve Final Results**
```bash
curl http://localhost:8000/api/v1/analysis/<analysis_id>
```

## Configuration

| Variable | Description |
| :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string. Default: `postgresql://postgres:postgres@postgres:5432/networkforge` |
| `REDIS_URL` | Redis connection string. Default: `redis://redis:6379/0` |
| `OPENAI_API_KEY` | Primary LLM key. Highly recommended for structured output speed. |
| `OLLAMA_BASE_URL` | URL to local Ollama instance (fallback). Default: `http://localhost:11434` |
| `TELEGRAM_BOT_TOKEN` | Required if you want push notifications to your mobile device. |

## Contributing

We move fast and value ruthless pragmatism over perfection.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Ensure your code passes tests (`make test`) and linting (`ruff check .`) before submitting.

## Roadmap

- [ ] Chrome extension integration for 1-click execution on LinkedIn profiles
- [ ] Email outreach formatting mode
- [ ] Direct ATS score checker integration
- [ ] Multi-language support for international outreach

## License

Distributed under the MIT License. See `LICENSE` for more information.
