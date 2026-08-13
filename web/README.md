# AcreOps field desk

Next.js 15 App Router workspace for the five AcreOps agents.

**Hosted interview demo:** Vercel Root Directory = `web` (`ACREOPS_API_URL` unset). Local equivalent below.

```bash
# Demo-only (no FastAPI, same path as Vercel)
make ui-demo
# http://127.0.0.1:3000

# Full stack, with the FastAPI service already running
make ui
```

The browser talks only to `/api/backend/*`. When `ACREOPS_API_URL` is configured,
that route proxies to FastAPI so the backend origin never has to be public.

If the Python service is absent or unreachable, the same route (and a client-side
fallback) switches to a deterministic, side-effect-free demo runtime. All five
workflows remain usable, including sample feasibility and drone PDF artifacts.

**Reset demo** in the header restores the desk and sample forms. The global banner
states that no email, SMS, PandaDoc, Airtable, Notion, or vendor dispatch happens.

```bash
cd web && npm run build && npm start
npm run smoke    # hits all five workflows + both PDFs
```
