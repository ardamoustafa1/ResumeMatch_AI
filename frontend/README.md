# ResumeMatch AI frontend

Next.js 16, React 19 and Tailwind CSS interface for ResumeMatch AI.

```bash
npm ci
npm run dev
```

The development server runs at <http://localhost:3000> and proxies `/api/*` to
`BACKEND_URL` (default `http://localhost:8000`). Set `NEXT_PUBLIC_WS_URL` when the
WebSocket API is hosted at another origin.

Quality checks:

```bash
npm run lint
npm test
npm run build
npm audit
```
