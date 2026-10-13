/**
 * POST /api/quote — the M&W GroundWorks lead endpoint.
 *
 * Lives on the site's own domain, so there is no CORS surface and no
 * dependency on a third party being reachable for a lead to be captured.
 *
 * Two independent things have to happen, and neither may block the other:
 *   1. Email the shop, so a human sees the job today. Sent through Resend from
 *      the verified true-site.tech domain -- Base44's mailer refuses to write
 *      to addresses that are not registered users of the app, which is why
 *      earlier notifications silently landed in the wrong inbox.
 *
 *      The shop is the ONLY recipient. This is not our business and its leads
 *      are not our mail; nobody at TrueSite is copied. Resend needs a verified
 *      domain to send FROM, never to authorise a recipient, so no DNS on
 *      mnwgroundworks.com is required for this to deliver.
 *   2. Persist the lead, so nothing depends on an inbox not being deleted.
 *
 * If either one succeeds the visitor gets a success state. Only if BOTH fail do
 * we return non-2xx, which makes main.js fall back to a pre-filled mailto so
 * the enquiry still has somewhere to go.
 */

const SHOP = 'mnwgroundworks@gmail.com';
const FROM = 'M&W GroundWorks Website <leads@true-site.tech>';
const STORE =
  'https://base44.app/api/apps/6a0a7846a08a2bd55b05e1fe/functions/mwGroundworksQuote';

const clean = (v, max = 2000) => (typeof v === 'string' ? v.trim().slice(0, max) : '');
const esc = (s) =>
  String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });

export async function onRequestPost({ request, env }) {
  const debug = new URL(request.url).searchParams.get('debug') === '1';
  // No recipient override: the shop is the only address this endpoint can mail.
  // (A ?to= param used to be honoured here, which let anyone send mail from
  // leads@true-site.tech to any address. Removed 2026-10-13.)
  const attempts = {};

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Expected JSON.' }, 400);
  }

  // Only a bot fills a field positioned off-canvas at zero opacity.
  // Look successful, store nothing, send nothing.
  if (clean(body.company)) return json({ ok: true });

  const name = clean(body.name, 120);
  const phone = clean(body.phone, 40);
  const email = clean(body.email, 160);
  const need = clean(body.need, 200);
  const town = clean(body.town, 160);
  const size = clean(body.size, 160);
  const detail = clean(body.detail || body.details || body.notes || body.message, 4000);
  const page = clean(body.page, 200);

  if (!name || (!phone && !email)) {
    return json({ error: 'Name plus a phone number or email address are required.' }, 400);
  }

  const subject = `New estimate request — ${name}${need ? ` (${need})` : ''}`;
  const rows = [
    ['Name', name],
    ['Phone', phone || '—'],
    ['Email', email || '—'],
    ['Service', need || '—'],
    ['Town / area', town || '—'],
    ['Property size', size || '—'],
  ];

  const text = [
    'New estimate request from the M&W GroundWorks website',
    '',
    ...rows.map(([k, v]) => `${k.padEnd(14)}: ${v}`),
    '',
    'Anything we should know:',
    detail || '—',
    '',
    `Page: ${page || '—'}`,
  ].join('\n');

  const html = `<div style="font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:640px">
<h2 style="margin:0 0 4px;font-size:19px">New estimate request</h2>
<p style="margin:0 0 18px;color:#666;font-size:14px">From the M&amp;W GroundWorks website</p>
<table cellpadding="0" cellspacing="0" style="border-collapse:collapse;width:100%;font-size:15px">
${rows
  .map(
    ([k, v]) => `<tr><td style="padding:7px 14px 7px 0;color:#666;white-space:nowrap;vertical-align:top">${esc(
      k,
    )}</td><td style="padding:7px 0;font-weight:600">${esc(v)}</td></tr>`,
  )
  .join('')}
</table>
${
  detail
    ? `<p style="margin:18px 0 4px;color:#666;font-size:14px">Anything we should know</p>
<div style="white-space:pre-wrap;background:#f6f6f4;border-left:3px solid #c8792a;padding:12px 14px;font-size:15px">${esc(
        detail,
      )}</div>`
    : ''
}
${
  email
    ? `<p style="margin:20px 0 0;font-size:14px;color:#666">Hit reply to answer ${esc(
        name,
      )} directly.</p>`
    : ''
}
<p style="margin:22px 0 0;color:#999;font-size:12px">Submitted from ${esc(page || '—')}</p>
</div>`;

  // --- 1. notify the shop
  let emailed = false;
  const key = env.RESEND_API_KEY;
  attempts.resend_key = key ? `present(${key.length})` : 'MISSING';

  if (key) {
    const payload = {
      from: FROM,
      to: [SHOP],
      subject,
      text,
      html,
    };
    if (email) payload.reply_to = email;

    try {
      const r = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const t = await r.text();
      attempts.resend = `${r.status} ${t.slice(0, 160)}`;
      emailed = r.ok;
    } catch (e) {
      attempts.resend = `threw ${String(e).slice(0, 160)}`;
    }
  }

  // --- 2. persist the lead (skip_email: the mail is already handled above)
  let stored = false;
  let leadId = null;
  try {
    const r = await fetch(STORE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Origin: 'https://mnwgroundworks.com' },
      body: JSON.stringify({
        name, phone, email, need, town, size, detail, page, skip_email: true,
      }),
    });
    const t = await r.text();
    attempts.store = `${r.status} ${t.slice(0, 160)}`;
    stored = r.ok;
    try { leadId = JSON.parse(t).id || null; } catch { /* not fatal */ }
  } catch (e) {
    attempts.store = `threw ${String(e).slice(0, 160)}`;
  }

  const out = { ok: emailed || stored, emailed, stored };
  if (leadId) out.id = leadId;
  if (debug) out.attempts = attempts;

  // Both paths dead: tell the browser, so it hands the lead to the mail client.
  return json(out, emailed || stored ? 200 : 502);
}

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: { Allow: 'POST, OPTIONS' } });
}

export async function onRequest() {
  return json({ error: 'Method not allowed' }, 405);
}
