// Elvesona – mottak av tilbakemeldinger (Cloudflare Worker)
//
// Tilbakemeldingssiden (elvesona.no/tilbakemelding/) er statisk og kan ikke ha et
// skrivetoken i HTML-en. Denne Workeren er det eneste leddet som holder tokenet:
// den validerer innsendingen og legger den til i tilbakemeldinger.json i et
// PRIVAT repo, slik at e-post og fritekst fra brukerne aldri blir offentlig.
//
// Hemmeligheter: GH_TOKEN settes med `wrangler secret put GH_TOKEN` – aldri her.
// Token: fine-grained PAT med Contents read/write KUN på REPO under.
// KV-binding RATE brukes til rate-limit (se wrangler.toml).

const OWNER = 'timon70-lab';
const REPO  = 'elvesona-tilbakemeldinger';
const PATH  = 'tilbakemeldinger.json';

const TILLATTE_ORIGINS = ['https://elvesona.no', 'https://www.elvesona.no'];
const LOKAL_ORIGIN = /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/;

const TYPER = ['ide', 'feil', 'fangst', 'annet'];
const MAKS_BODY = 10000;       // tegn
const MAKS_PER_TIME = 5;       // innsendinger per IP per time
const MAKS_FORSOK = 5;         // skriveforsøk ved sha-konflikt

function originTillatt(origin) {
  return !!origin && (TILLATTE_ORIGINS.includes(origin) || LOKAL_ORIGIN.test(origin));
}

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

function svar(status, data, origin) {
  const headers = { 'Content-Type': 'application/json; charset=utf-8' };
  if (origin) Object.assign(headers, corsHeaders(origin));
  return new Response(JSON.stringify(data), { status, headers });
}

// ── base64 <-> UTF-8 (æøå må overleve begge veier) ────────────────────────
function b64TilTekst(b64) {
  const bin = atob(b64.replace(/\n/g, ''));
  const bytes = Uint8Array.from(bin, c => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

function tekstTilB64(tekst) {
  const bytes = new TextEncoder().encode(tekst);
  let bin = '';
  for (let i = 0; i < bytes.length; i += 0x8000) {
    bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  }
  return btoa(bin);
}

async function sha256Hex(tekst) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(tekst));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
}

// ── Validering ─────────────────────────────────────────────────────────────
function strFelt(v, maks) {
  if (v === undefined || v === null) return '';
  if (typeof v !== 'string') return null;
  const t = v.trim();
  return t.length > maks ? null : t;
}

function valider(body) {
  if (!body || typeof body !== 'object') return { feil: 'Ugyldig innhold.' };
  const type = strFelt(body.type, 20);
  if (!TYPER.includes(type)) return { feil: 'Ukjent type.' };
  const melding = strFelt(body.melding, 2000);
  if (melding === null) return { feil: 'Meldingen er for lang (maks 2000 tegn).' };
  if (melding.length < 5) return { feil: 'Meldingen er for kort.' };
  const epost = strFelt(body.epost, 200);
  if (epost === null || (epost && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(epost))) {
    return { feil: 'Ugyldig e-postadresse.' };
  }
  const elv = strFelt(body.elv, 60);
  const sone = strFelt(body.sone, 60);
  const side = strFelt(body.side, 200);
  const versjon = strFelt(body.versjon, 20);
  if ([elv, sone, side, versjon].includes(null)) return { feil: 'Et av feltene er for langt.' };
  return { post: { type, elv, sone, melding, epost, side, versjon } };
}

// ── Rate-limit (KV, rullerende time) ──────────────────────────────────────
async function overGrensen(env, ip) {
  if (!env.RATE || !ip) return false;
  const nokkel = 'ip:' + (await sha256Hex(ip));
  const n = parseInt((await env.RATE.get(nokkel)) || '0', 10);
  if (n >= MAKS_PER_TIME) return true;
  await env.RATE.put(nokkel, String(n + 1), { expirationTtl: 3600 });
  return false;
}

// ── GitHub Contents API ───────────────────────────────────────────────────
function ghHeaders(env) {
  return {
    'Authorization': 'Bearer ' + env.GH_TOKEN,
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'User-Agent': 'elvesona-tilbakemelding-worker',
  };
}

const API = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${PATH}`;

async function lagre(env, post) {
  for (let forsok = 1; forsok <= MAKS_FORSOK; forsok++) {
    const res = await fetch(API, { headers: ghHeaders(env) });
    let liste = [], sha = null;
    if (res.ok) {
      const gd = await res.json();
      liste = JSON.parse(b64TilTekst(gd.content));
      sha = gd.sha;
      if (!Array.isArray(liste)) throw new Error('tilbakemeldinger.json er ikke en liste');
    } else if (res.status !== 404) {
      throw new Error('GitHub GET ' + res.status);
    }

    liste.push(post);
    const body = {
      message: 'Tilbakemelding ' + post.id,
      content: tekstTilB64(JSON.stringify(liste, null, 2) + '\n'),
    };
    if (sha) body.sha = sha;

    const put = await fetch(API, {
      method: 'PUT',
      headers: { ...ghHeaders(env), 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (put.ok) return;
    // 409/422: fila ble endret mellom GET og PUT (samtidig innsending) – prøv igjen med fersk sha
    if ((put.status === 409 || put.status === 422) && forsok < MAKS_FORSOK) {
      await new Promise(r => setTimeout(r, 300 * forsok + Math.random() * 300));
      continue;
    }
    throw new Error('GitHub PUT ' + put.status);
  }
}

// ── Inngang ────────────────────────────────────────────────────────────────
export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin');
    if (!originTillatt(origin)) return svar(403, { ok: false, feil: 'Ikke tillatt.' });

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }
    if (request.method !== 'POST') return svar(405, { ok: false, feil: 'Kun POST.' }, origin);

    const tekst = await request.text();
    if (tekst.length > MAKS_BODY) return svar(413, { ok: false, feil: 'For stor innsending.' }, origin);

    let body;
    try { body = JSON.parse(tekst); } catch (e) {
      return svar(400, { ok: false, feil: 'Ugyldig JSON.' }, origin);
    }

    // Honeypot: skjult felt som bare roboter fyller ut. Late som alt gikk bra.
    if (body && typeof body.website === 'string' && body.website.trim() !== '') {
      return svar(200, { ok: true }, origin);
    }

    const { feil, post } = valider(body);
    if (feil) return svar(400, { ok: false, feil }, origin);

    if (await overGrensen(env, request.headers.get('CF-Connecting-IP'))) {
      return svar(429, { ok: false, feil: 'For mange innsendinger. Prøv igjen senere.' }, origin);
    }

    if (!env.GH_TOKEN) return svar(500, { ok: false, feil: 'Mottaket er ikke konfigurert.' }, origin);

    const naa = new Date();
    const id = 'T-' + naa.getTime() + '-' + Math.random().toString(36).slice(2, 6);
    const full = { id, mottatt: naa.toISOString(), status: 'ny', ...post };
    try {
      await lagre(env, full);
    } catch (e) {
      console.log('Lagring feilet:', e.message);
      return svar(502, { ok: false, feil: 'Kunne ikke lagre akkurat nå.' }, origin);
    }
    return svar(200, { ok: true, id: full.id }, origin);
  },
};
