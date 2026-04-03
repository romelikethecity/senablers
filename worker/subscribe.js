/**
 * Cloudflare Worker: Newsletter Signup -> Resend Audience
 *
 * Receives POST with { email } from the site's inline signup forms,
 * adds the contact to a Resend audience, and returns JSON.
 *
 * Environment variables (set via `wrangler secret put`):
 *   RESEND_API_KEY   - your Resend API key
 *   RESEND_AUDIENCE_ID - the audience ID from Resend dashboard
 *
 * Deploy:
 *   cd worker && npx wrangler deploy
 */

const ALLOWED_ORIGINS = [
  'https://senablers.com',
  'https://www.senablers.com',
  'http://localhost:8090',
];

function corsHeaders(origin) {
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...corsHeaders(origin), 'Content-Type': 'application/json' },
      });
    }

    try {
      const body = await request.json();
      const email = (body.email || '').trim().toLowerCase();

      if (!email || !email.includes('@') || !email.includes('.')) {
        return new Response(JSON.stringify({ error: 'Valid email required' }), {
          status: 400,
          headers: { ...corsHeaders(origin), 'Content-Type': 'application/json' },
        });
      }

      // Add contact to Resend audience
      const res = await fetch(`https://api.resend.com/audiences/${env.RESEND_AUDIENCE_ID}/contacts`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.RESEND_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          unsubscribed: false,
        }),
      });

      if (!res.ok) {
        const err = await res.text();
        console.error('Resend error:', res.status, err);
        return new Response(JSON.stringify({ error: 'Signup failed. Please try again.' }), {
          status: 502,
          headers: { ...corsHeaders(origin), 'Content-Type': 'application/json' },
        });
      }

      return new Response(JSON.stringify({ success: true, message: 'Subscribed!' }), {
        status: 200,
        headers: { ...corsHeaders(origin), 'Content-Type': 'application/json' },
      });
    } catch (e) {
      console.error('Worker error:', e);
      return new Response(JSON.stringify({ error: 'Something went wrong' }), {
        status: 500,
        headers: { ...corsHeaders(origin), 'Content-Type': 'application/json' },
      });
    }
  },
};
