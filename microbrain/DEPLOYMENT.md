# Deployment

## Database

Create a PostgreSQL database in Supabase or Neon.

Set:

```txt
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DB
```

## Backend

Deploy `microbrain/backend` to Render, Railway, or Fly.io.

Start command:

```sh
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The API creates tables at startup through SQLAlchemy metadata.

## Frontend

Deploy `microbrain/frontend` to Netlify.

For drag-and-drop deploys, upload the built contents of `microbrain/frontend/dist`, not the full `microbrain` source folder.

Build command:

```sh
npm run build
```

Publish directory:

```txt
dist
```

Environment:

```txt
VITE_API_BASE=https://YOUR_BACKEND_URL
```

If `VITE_API_BASE` is not set, the UI still renders and shows `api not configured`, but turns will not be processed.
