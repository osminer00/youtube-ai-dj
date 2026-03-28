# YouTube AI DJ

Version: `v0.2.4`

Latest release note: `v0.2.4 - Switched youtube playback to hosted https player. Currently video player is working with skip and previous song buttons. play pause button currently only restarts the song (needs changing, play pause can be handled by the video player)`

This is the YouTube-first edition of AI DJ. It is the lane for:

- personal music video recommendation experiments
- YouTube search, ranking, and queueing
- official embedded YouTube playback inside the AI DJ shell

## Cloudflare deployment shape

For a shared or public deployment, use:

- Cloudflare Pages for the static frontend
- a Cloudflare Worker for `/search`
- a Worker secret named `YOUTUBE_API_KEY`
- an allowed origin variable matching your Pages URL

The frontend now supports two search modes:

- direct browser mode with a pasted YouTube Data API key
- proxy mode with a hosted Worker URL in `Search Proxy URL`

## Current state

- Framework transfer started from the earlier private-edition shell
- Standalone player shell created
- YouTube search, queue, and embed flow scaffolded
- Personal recommendation flow is being shaped around official YouTube playback

## Run it

```powershell
python start.py
```

Then open `http://127.0.0.1:8891/index.html`.

## Run the proxy locally

1. Install Wrangler once:

```powershell
npm install -g wrangler
```

2. Create `.dev.vars` from `.dev.vars.example` and put in your YouTube key.
3. Start the Worker from the project root:

```powershell
wrangler dev
```

4. In the app, set `Search Proxy URL` to `http://127.0.0.1:8787`.
5. Run `python start.py` and open `http://127.0.0.1:8891/index.html`.

Local development is already allowed by `ALLOWED_ORIGIN_DEV` in [wrangler.toml](/c:/Users/n3mog/Documents/ai/ai%20dj/projects/youtube-ai-dj/wrangler.toml).

## Deploy with Cloudflare

1. Create a Cloudflare Pages project from this repo and publish the project root as static files.
2. Deploy the Worker in [cloudflare/search-proxy.js](/c:/Users/n3mog/Documents/ai/ai%20dj/projects/youtube-ai-dj/cloudflare/search-proxy.js).
3. Add the Worker secret `YOUTUBE_API_KEY`.
4. Set `ALLOWED_ORIGIN` in [wrangler.toml](/c:/Users/n3mog/Documents/ai/ai%20dj/projects/youtube-ai-dj/wrangler.toml) to your Pages origin, then deploy.
5. Paste the deployed Worker URL into the app's `Search Proxy URL` field and leave the browser API key blank.

Example Worker commands:

```powershell
npm install -g wrangler
wrangler secret put YOUTUBE_API_KEY
wrangler deploy
```

If you prefer repo scripts:

```powershell
npm run cf:dev
npm run cf:deploy
```

The Worker accepts requests like:

```text
https://your-worker-subdomain.workers.dev/search?q=daft+punk+official
```

That keeps the YouTube key out of the browser while preserving the same result flow in the app.

## Recommended Cloudflare layout

- Cloudflare Pages:
  publish this repo root as the static site
- Cloudflare Worker:
  deploy [cloudflare/search-proxy.js](/c:/Users/n3mog/Documents/ai/ai%20dj/projects/youtube-ai-dj/cloudflare/search-proxy.js)
- Frontend app:
  store your Worker URL in the app's `Search Proxy URL` field

For production, set `ALLOWED_ORIGIN` to the exact Pages domain you ship from. For local testing, keep `ALLOWED_ORIGIN_DEV` pointed at `http://127.0.0.1:8891`.

## Backups

- Timestamped local backup saved at `backups/20260328-093045/`

## Changelog

- See [CHANGELOG.md](/c:/Users/n3mog/Documents/ai/ai%20dj/projects/youtube-ai-dj/CHANGELOG.md)

## What tomorrow should focus on

1. Verify YouTube API search and embed flow with your key.
2. Improve result ranking toward official uploads and stronger match quality.
3. Add local taste signals so recommendations improve over time.
4. Keep the scope centered on personal use and official embedded playback.




