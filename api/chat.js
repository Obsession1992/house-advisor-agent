import { PassThrough } from 'stream';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const response = await fetch('https://api.coze.cn/v2/chat/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': req.headers['authorization'] || '',
      },
      body: JSON.stringify(req.body),
    });

    const contentType = response.headers.get('content-type') || '';

    if (contentType.includes('text/event-stream')) {
      res.setHeader('Content-Type', 'text/event-stream');
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Connection', 'keep-alive');
      res.status(200);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      const passthrough = new PassThrough();

      (async () => {
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            passthrough.write(decoder.decode(value, { stream: true }));
          }
          passthrough.end();
        } catch (err) {
          passthrough.destroy(err);
        }
      })();

      passthrough.pipe(res);
    } else {
      const data = await response.json();
      return res.status(response.status).json(data);
    }
  } catch (err) {
    return res.status(502).json({ error: err.message });
  }
}
