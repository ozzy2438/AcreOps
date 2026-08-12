# AcreOps field desk

Next.js 15 App Router workspace for the five AcreOps agents.

```bash
# from repo root, with the FastAPI service already running
make ui
# http://127.0.0.1:3000
```

The browser talks only to `/api/backend/*`. That route handler proxies to `ACREOPS_API_URL` (default `http://127.0.0.1:8000`) so the FastAPI origin never has to be public.
