# AcreOps field desk

Next.js 15 App Router workspace for the five AcreOps agents.

```bash
# from repo root, with the FastAPI service already running
make ui
# http://127.0.0.1:3000
```

The browser talks only to `/api/backend/*`. When `ACREOPS_API_URL` is configured,
that route proxies to FastAPI so the backend origin never has to be public.

## Interactive preview

If `ACREOPS_API_URL` is absent, the same route switches to a deterministic,
side-effect-free demo runtime. All five workflows remain usable in a hosted preview,
including sample feasibility and drone PDF artifacts. The global demo banner makes it
clear that no email, SMS, signature, permit, schedule, or tenant record is changed.
