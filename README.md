# YouTube AI DJ

This is the new YouTube-first edition of AI DJ. It is the lane for:

- shareable music video playback
- future AI-generated fallback visuals when no official video exists
- an eventual mobile-friendly and iOS-friendly hosted app

## Current state

- Framework transfer started from the Spotify edition
- Standalone player shell created
- YouTube search, queue, and embed flow scaffolded
- AI-generated video lane documented, not implemented yet

## Run it

```powershell
python start.py
```

Then open `http://127.0.0.1:8891/index.html`.

## What tomorrow should focus on

1. Verify YouTube API search and embed flow with your key.
2. Decide which Spotify-era controls stay in the shared framework.
3. Add backend support for AI-generated fallback video jobs.
4. Plan hosted auth/storage so this can move toward iOS use.
