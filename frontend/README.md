# PAISAI Frontend

The PAISAI web client — Next.js (App Router) + TypeScript + Tailwind, built to the
[design language](../docs/DESIGN_LANGUAGE.md): Bloomberg Terminal meets Apple, and
engineered so the founding principles are *visible*. Provenance chips let a user
tell fact from forecast at a glance; missing data renders as an honest "No verified
data," never a fabricated figure.

## Run locally

```bash
cd frontend
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
```

## Deploy on Vercel

This app lives in the `frontend/` subdirectory of the repository, so Vercel needs
to be pointed at it.

**Dashboard (recommended)**
1. Import the GitHub repo `GyaanShetty/PAISAI` at <https://vercel.com/new>.
2. Set **Root Directory** to `frontend`.
3. Framework preset is detected automatically as **Next.js** (also pinned in
   [`vercel.json`](vercel.json)). Build command `next build`, output `.next`.
4. Deploy. No environment variables are required for this foundational build.

**Vercel CLI**
```bash
npm i -g vercel
cd frontend
vercel            # first run links the project; set root dir to the current folder
vercel --prod     # promote to production
```

> **Note on the monorepo:** the Python backend (`../backend`) is *not* deployed by
> Vercel here — Vercel builds only the `frontend/` root directory. The backend
> (FastAPI) is deployed separately per [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).
> When the frontend needs to call it, add `NEXT_PUBLIC_API_BASE_URL` in the Vercel
> project settings; see [`.env.example`](.env.example).

## Structure

```
frontend/
├── app/
│   ├── layout.tsx        # root layout, metadata
│   ├── page.tsx          # landing: principles + provenance demonstration
│   └── globals.css       # base styles; tabular figures
├── components/
│   ├── Wordmark.tsx      # PAIS·AI wordmark (AI highlighted)
│   └── ProvenanceChip.tsx# provenance chips, provenanced figure, "Unavailable"
├── tailwind.config.ts    # muted institutional palette; provenance accents
├── vercel.json           # Vercel/Next.js build config
└── package.json
```
