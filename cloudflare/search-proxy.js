const YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search';
const YOUTUBE_VIDEOS_URL = 'https://www.googleapis.com/youtube/v3/videos';

function isAllowedOrigin(origin, env) {
  if (!origin) return false;
  return [env.ALLOWED_ORIGIN, env.ALLOWED_ORIGIN_DEV]
    .filter(Boolean)
    .includes(origin);
}

function buildCorsHeaders(origin, env) {
  const allowOrigin = isAllowedOrigin(origin, env) ? origin : (env.ALLOWED_ORIGIN || '*');
  return {
    'Access-Control-Allow-Origin': allowOrigin,
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  };
}

function json(data, status, headers) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=60',
      ...headers
    }
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const corsHeaders = buildCorsHeaders(origin, env);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    if (request.method !== 'GET') {
      return json({ error: { message: 'Method not allowed.' } }, 405, corsHeaders);
    }

    const url = new URL(request.url);
    if (url.pathname !== '/search' && url.pathname !== '/video') {
      return json({ error: { message: 'Not found.' } }, 404, corsHeaders);
    }

    const upstreamUrl = new URL(url.pathname === '/search' ? YOUTUBE_SEARCH_URL : YOUTUBE_VIDEOS_URL);
    if (url.pathname === '/search') {
      const query = url.searchParams.get('q')?.trim() || '';
      if (!query) {
        return json({ error: { message: 'Missing search query.' } }, 400, corsHeaders);
      }
      upstreamUrl.search = new URLSearchParams({
        part: 'snippet',
        maxResults: '8',
        q: query,
        type: 'video',
        videoEmbeddable: 'true',
        key: env.YOUTUBE_API_KEY
      }).toString();
    } else {
      const videoId = url.searchParams.get('id')?.trim() || '';
      if (!videoId) {
        return json({ error: { message: 'Missing video id.' } }, 400, corsHeaders);
      }
      upstreamUrl.search = new URLSearchParams({
        part: 'snippet,status',
        id: videoId,
        key: env.YOUTUBE_API_KEY
      }).toString();
    }

    const upstream = await fetch(upstreamUrl, {
      headers: {
        'Accept': 'application/json'
      },
      cf: {
        cacheTtl: 60,
        cacheEverything: true
      }
    });

    const payload = await upstream.json();
    return json(payload, upstream.status, corsHeaders);
  }
};
