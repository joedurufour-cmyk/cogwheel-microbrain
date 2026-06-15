# Deploy Cogwheel from GitHub to Netlify

Use this when mobile drag-and-drop does not work.

## Netlify settings

If Netlify reads this repository, `netlify.toml` already sets:

```txt
base = microbrain/frontend
build command = npm run build
publish directory = dist
```

## Steps

1. Push this workspace to GitHub.
2. In Netlify, choose **Add new project**.
3. Choose **Import an existing project**.
4. Select the GitHub repo.
5. Keep the detected settings from `netlify.toml`.
6. Deploy.

## Backend note

The frontend renders without a backend and shows `api not configured`.

When the FastAPI backend is deployed, add this Netlify environment variable:

```txt
VITE_API_BASE=https://YOUR_BACKEND_URL
```
