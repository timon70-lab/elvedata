/* felles/registrering.js — feltregistrering av punkter i elvekartene.
 *
 * Bare for Per Lasse: dashbordene laster denne fila kun når GitHub-tokenet fra
 * adminpanelet ligger i nettleseren (localStorage 'elvedata_admin_token').
 * Vanlige brukere laster den aldri.
 *
 * Punkter (sonegrense-skilt, parkering, desinfisering, kortsalg, annet) lagres i
 * det PRIVATE repoet elvesona-tilbakemeldinger, fila punkter.json. De er
 * ubekreftede feltnotater og publiseres ikke. Adminpanelet viser lista, og
 * punktene gjøres om til ekte data (ZONE_COORDS, steder_<elv>.json,
 * desinfisering.json) for hånd.
 *
 * Uten nett legges punktet i kø i localStorage og sendes når nettet er tilbake.
 *
 * Bruker globale navn fra dashbordet: map, ZONES, SESONG_ELV, soneVedPunkt.
 */
(function () {
  'use strict';
  var TOKEN_KEY = 'elvedata_admin_token';
  var KO_KEY = 'elvesona_punkt_ko';
  var API = 'https://api.github.com/repos/timon70-lab/elvesona-tilbakemeldinger/contents/punkter.json';
  var TYPER = {
    grense: '🚩 Sonegrense / skilt',
    parkering: '🅿️ Parkering',
    desinfisering: '🧴 Desinfisering',
    kortsalg: '🎫 Kortsalg',
    annet: '📝 Annet'
  };

  function token() { try { return localStorage.getItem(TOKEN_KEY) || ''; } catch (e) { return ''; } }
  if (!token()) return;

  // Dashbordets toppnivå-let/const er ikke egenskaper på window; indirekte eval leser dem.
  function g(navn) { try { return (0, eval)(navn); } catch (e) { return undefined; } }
  function elv() { return g('SESONG_ELV') || location.pathname.split('/').filter(Boolean)[0] || ''; }

  // ---------------------------------------------------------------- stil
  var css = document.createElement('style');
  css.textContent = [
    '.reg-knapp{background:#ed8936!important;color:#1a202c!important;border:2px solid rgba(0,0,0,0.2)!important;border-radius:4px;padding:5px 10px;font-size:0.75rem;font-weight:700;cursor:pointer;font-family:inherit;white-space:nowrap;}',
    '.reg-sikte{position:absolute;left:50%;top:50%;width:44px;height:44px;margin:-22px 0 0 -22px;z-index:650;pointer-events:none;display:none;}',
    '.reg-sikte:before,.reg-sikte:after{content:"";position:absolute;background:#ed8936;box-shadow:0 0 0 1px #fff;}',
    '.reg-sikte:before{left:21px;top:0;width:2px;height:44px;}',
    '.reg-sikte:after{top:21px;left:0;height:2px;width:44px;}',
    '.reg-modus .reg-sikte{display:block;}',
    '.reg-bar{position:absolute;left:50%;bottom:96px;transform:translateX(-50%);z-index:1001;display:none;gap:6px;flex-wrap:wrap;justify-content:center;background:rgba(26,32,44,0.88);padding:6px 8px;border-radius:10px;width:max-content;max-width:calc(100% - 20px);}',
    '.reg-modus .reg-bar{display:flex;}',
    '.reg-bar .reg-tekst{width:100%;color:#fff;font-size:0.68rem;text-align:center;}',
    '.reg-bar button{border:none;border-radius:6px;padding:7px 10px;white-space:nowrap;font-size:0.76rem;font-weight:700;cursor:pointer;font-family:inherit;}',
    '.reg-bar .ok{background:#ed8936;color:#1a202c;} .reg-bar .gps{background:#fff;color:#1a202c;} .reg-bar .avbryt{background:#4a5568;color:#fff;}',
    '.reg-bakgrunn{position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,0.45);display:flex;align-items:center;justify-content:center;padding:12px;}',
    '.reg-skjema{background:#fff;border-radius:12px;padding:16px;width:380px;max-width:100%;max-height:calc(100vh - 24px);overflow:auto;font-family:inherit;color:#1a202c;box-shadow:0 8px 30px rgba(0,0,0,0.35);}',
    '.reg-skjema h3{margin:0 0 4px;font-size:1rem;}',
    '.reg-skjema .reg-pos{font-size:0.72rem;color:#4a5568;margin-bottom:10px;}',
    '.reg-skjema label{display:block;font-size:0.72rem;font-weight:700;margin:10px 0 4px;color:#2d3748;}',
    '.reg-skjema select,.reg-skjema textarea{width:100%;box-sizing:border-box;font:inherit;font-size:16px;padding:8px;border:1px solid #cbd5e0;border-radius:6px;}',
    '.reg-skjema textarea{min-height:90px;resize:vertical;}',
    '.reg-skjema .reg-knapper{display:flex;gap:8px;justify-content:flex-end;margin-top:14px;}',
    '.reg-skjema .reg-knapper button{border:none;border-radius:6px;padding:9px 14px;font-weight:700;cursor:pointer;font-family:inherit;}',
    '.reg-skjema .lagre{background:#276749;color:#fff;} .reg-skjema .avbryt{background:#e2e8f0;color:#1a202c;}',
    '.reg-melding{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:10001;background:#1a202c;color:#fff;padding:9px 14px;border-radius:8px;font-size:0.8rem;max-width:calc(100vw - 32px);box-shadow:0 4px 14px rgba(0,0,0,0.3);}',
    '.reg-pin{width:14px;height:14px;border-radius:50%;background:#ed8936;border:2px solid #fff;box-shadow:0 0 0 1px #1a202c;}',
    '.reg-pin.ko{background:#a0aec0;}',
    '.reg-pin.behandlet{background:#68d391;}'
  ].join('\n');
  document.head.appendChild(css);

  function rot() { return document.fullscreenElement || document.body; }

  var meldTimer = null, meldEl = null;
  function melding(tekst, ms) {
    if (!meldEl) { meldEl = document.createElement('div'); meldEl.className = 'reg-melding'; }
    meldEl.textContent = tekst;
    rot().appendChild(meldEl);
    clearTimeout(meldTimer);
    meldTimer = setTimeout(function () { meldEl.remove(); }, ms || 4000);
  }

  // ---------------------------------------------------------------- kø og GitHub
  function lesKo() { try { return JSON.parse(localStorage.getItem(KO_KEY) || '[]'); } catch (e) { return []; } }
  function skrivKo(ko) { try { localStorage.setItem(KO_KEY, JSON.stringify(ko)); } catch (e) { /* full eller blokkert */ } }

  function b64Til(tekst) { return btoa(unescape(encodeURIComponent(tekst))); }
  function b64Fra(b64) { return decodeURIComponent(escape(atob(b64.replace(/\n/g, '')))); }
  function hoder() { return { 'Authorization': 'Bearer ' + token(), 'Accept': 'application/vnd.github+json' }; }

  function hentFil() {
    return fetch(API, { headers: hoder(), cache: 'no-store' }).then(function (r) {
      if (r.status === 404) return { liste: [], sha: null, mangler: true };
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json().then(function (d) { return { liste: JSON.parse(b64Fra(d.content)), sha: d.sha }; });
    });
  }

  function skrivFil(liste, sha, tekst) {
    var body = { message: tekst, content: b64Til(JSON.stringify(liste, null, 2) + '\n') };
    if (sha) body.sha = sha;
    return fetch(API, {
      method: 'PUT',
      headers: Object.assign({ 'Content-Type': 'application/json' }, hoder()),
      body: JSON.stringify(body)
    }).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); });
  }

  var sender = false;
  function sendKo(forsok) {
    var ko = lesKo();
    if (!ko.length || sender) return Promise.resolve();
    if (navigator.onLine === false) return Promise.resolve();
    sender = true;
    return hentFil().then(function (f) {
      var ider = {};
      f.liste.forEach(function (p) { ider[p.id] = true; });
      var nye = ko.filter(function (p) { return !ider[p.id]; });
      if (!nye.length) return f.liste;
      var liste = f.liste.concat(nye);
      return skrivFil(liste, f.sha, 'Feltpunkt ' + nye.map(function (p) { return p.id; }).join(', '))
        .then(function () { return liste; });
    }).then(function (liste) {
      // Fjern bare det som faktisk ble sendt: nye punkter kan ha kommet i køen i mellomtiden.
      var sendt = {};
      liste.forEach(function (p) { sendt[p.id] = true; });
      skrivKo(lesKo().filter(function (p) { return !sendt[p.id]; }));
      sender = false;
      melding('✓ Punktet er lagret i elvesona-tilbakemeldinger.');
      visPunkter(liste);
    }).catch(function (e) {
      sender = false;
      // 409 = noen andre skrev samtidig: prøv én gang til med fersk sha.
      if (/409|422/.test(e.message) && !forsok) return sendKo(1);
      var auth = /HTTP (401|403|404)/.test(e.message);
      melding(auth ? '⚠️ Tokenet mangler tilgang til elvesona-tilbakemeldinger (' + e.message + '). Punktet ligger i kø på denne enheten.'
                   : '📶 Ingen kontakt med GitHub. Punktet ligger i kø og sendes når du har nett.', 6000);
      visPunkter(null);
    });
  }
  window.addEventListener('online', function () { sendKo(); });

  // ---------------------------------------------------------------- punkter i kartet
  var lag = null, sisteListe = [];
  function visPunkter(liste) {
    var m = g('map');
    if (!m) return;
    if (liste) sisteListe = liste;
    if (!lag) lag = L.layerGroup().addTo(m);
    lag.clearLayers();
    var e = elv();
    var alle = sisteListe.filter(function (p) { return p.elv === e && p.status !== 'slettet'; })
      .map(function (p) { return [p, p.status === 'behandlet' ? 'behandlet' : '']; })
      .concat(lesKo().filter(function (p) { return p.elv === e; }).map(function (p) { return [p, 'ko']; }));
    alle.forEach(function (par) {
      var p = par[0];
      var mk = L.marker([p.lat, p.lon], {
        icon: L.divIcon({ className: '', html: '<div class="reg-pin ' + par[1] + '"></div>', iconSize: [18, 18], iconAnchor: [9, 9] }),
        zIndexOffset: 900
      });
      var div = document.createElement('div');
      div.style.cssText = 'font-size:0.75rem;max-width:230px;';
      var b = document.createElement('b'); b.textContent = TYPER[p.type] || p.type; div.appendChild(b);
      [p.sone || 'Ingen sone', p.kommentar || '',
       new Date(p.registrert).toLocaleString('no-NO', { dateStyle: 'short', timeStyle: 'short' })
         + (p.noyaktighet_m ? ' · GPS ±' + p.noyaktighet_m + ' m' : ' · plassert i kartet')
         + (par[1] === 'ko' ? ' · i kø' : par[1] === 'behandlet' ? ' · behandlet' : '')
      ].forEach(function (t) { if (!t) return; var d = document.createElement('div'); d.textContent = t; d.style.marginTop = '3px'; div.appendChild(d); });
      mk.bindPopup(div);
      mk.addTo(lag);
    });
  }

  // ---------------------------------------------------------------- skjema
  function apneSkjema(lat, lon, noyaktighet) {
    var finnSone = g('soneVedPunkt');
    var sone = (typeof finnSone === 'function' && finnSone(lat, lon)) || '';
    var soner = g('ZONES') || [];

    var bak = document.createElement('div'); bak.className = 'reg-bakgrunn';
    var f = document.createElement('div'); f.className = 'reg-skjema'; bak.appendChild(f);
    var h = document.createElement('h3'); h.textContent = '📍 Nytt feltpunkt'; f.appendChild(h);
    var pos = document.createElement('div'); pos.className = 'reg-pos';
    pos.textContent = lat.toFixed(6) + ', ' + lon.toFixed(6) + (noyaktighet ? ' · GPS ±' + noyaktighet + ' m' : ' · plassert i kartet');
    f.appendChild(pos);

    function felt(tekst, el) { var l = document.createElement('label'); l.textContent = tekst; f.appendChild(l); f.appendChild(el); return el; }
    var type = felt('Type', document.createElement('select'));
    Object.keys(TYPER).forEach(function (k) { type.add(new Option(TYPER[k], k)); });
    var soneSel = felt('Sone', document.createElement('select'));
    soneSel.add(new Option('Ingen / usikker', ''));
    soner.forEach(function (z) { soneSel.add(new Option(z, z)); });
    soneSel.value = sone;
    var kommentar = felt('Kommentar', document.createElement('textarea'));
    kommentar.placeholder = 'F.eks. «Skilt: grense Sone 4/5, østsiden» eller «Parkering for 6 biler»';

    var knapper = document.createElement('div'); knapper.className = 'reg-knapper'; f.appendChild(knapper);
    var avbryt = document.createElement('button'); avbryt.className = 'avbryt'; avbryt.textContent = 'Avbryt';
    var lagre = document.createElement('button'); lagre.className = 'lagre'; lagre.textContent = 'Lagre punkt';
    knapper.appendChild(avbryt); knapper.appendChild(lagre);

    avbryt.onclick = function () { bak.remove(); };
    lagre.onclick = function () {
      var na = new Date();
      var p = {
        id: 'p' + na.toISOString().replace(/\D/g, '').slice(2, 14) + Math.random().toString(36).slice(2, 5),
        elv: elv(),
        type: type.value,
        sone: soneSel.value || null,
        lat: Math.round(lat * 1e6) / 1e6,
        lon: Math.round(lon * 1e6) / 1e6,
        noyaktighet_m: noyaktighet || null,
        kilde: noyaktighet ? 'gps' : 'kart',
        kommentar: kommentar.value.trim(),
        registrert: na.toISOString(),
        status: 'ny',
        side: location.pathname
      };
      var ko = lesKo(); ko.push(p); skrivKo(ko);
      bak.remove();
      avsluttModus();
      melding('⏳ Lagrer punktet …');
      visPunkter(null);
      sendKo();
    };
    rot().appendChild(bak);
    kommentar.focus();
  }

  // ---------------------------------------------------------------- markeringsmodus
  var beholder = null, knapp = null, gpsVakt = null;
  function startModus() {
    beholder.classList.add('reg-modus');
    knapp.textContent = '✕ Avslutt markering';
  }
  function avsluttModus() {
    if (!beholder) return;
    beholder.classList.remove('reg-modus');
    knapp.textContent = '➕ Marker punkt';
    if (gpsVakt !== null) { navigator.geolocation.clearWatch(gpsVakt); gpsVakt = null; }
  }

  // GPS: følg posisjonen i opptil 20 s og bruk den beste målingen (de første er ofte grove).
  function brukGps(gpsKnapp) {
    if (!navigator.geolocation) { melding('Nettleseren gir ikke posisjon.'); return; }
    var best = null, start = Date.now();
    gpsKnapp.textContent = '⏳ GPS …';
    function ferdig() {
      if (gpsVakt !== null) { navigator.geolocation.clearWatch(gpsVakt); gpsVakt = null; }
      gpsKnapp.textContent = '📍 GPS';
      if (!best) { melding('Fant ikke posisjonen. Er posisjon slått på?'); return; }
      var c = best.coords;
      g('map').setView([c.latitude, c.longitude], Math.max(g('map').getZoom(), 17));
      apneSkjema(c.latitude, c.longitude, Math.max(1, Math.round(c.accuracy)));
    }
    gpsVakt = navigator.geolocation.watchPosition(function (p) {
      if (!best || p.coords.accuracy < best.coords.accuracy) best = p;
      gpsKnapp.textContent = '⏳ ±' + Math.round(best.coords.accuracy) + ' m';
      if (best.coords.accuracy <= 8 || Date.now() - start > 20000) ferdig();
    }, function () { ferdig(); }, { enableHighAccuracy: true, maximumAge: 0, timeout: 20000 });
    setTimeout(function () { if (gpsVakt !== null) ferdig(); }, 21000);
  }

  function init(m) {
    beholder = m.getContainer();
    var sikte = document.createElement('div'); sikte.className = 'reg-sikte'; beholder.appendChild(sikte);

    var bar = document.createElement('div'); bar.className = 'reg-bar';
    var t = document.createElement('div'); t.className = 'reg-tekst';
    t.textContent = 'Flytt kartet så krysset står på punktet';
    var ok = document.createElement('button'); ok.className = 'ok'; ok.textContent = '✓ Marker her';
    var gps = document.createElement('button'); gps.className = 'gps'; gps.textContent = '📍 GPS';
    var av = document.createElement('button'); av.className = 'avbryt'; av.textContent = 'Avbryt';
    [t, ok, gps, av].forEach(function (el) { bar.appendChild(el); });
    beholder.appendChild(bar);
    L.DomEvent.disableClickPropagation(bar);
    ok.onclick = function () { var c = m.getCenter(); apneSkjema(c.lat, c.lng, null); };
    gps.onclick = function () { brukGps(gps); };
    av.onclick = avsluttModus;

    var Knapp = L.Control.extend({
      options: { position: 'topright' },
      onAdd: function () {
        knapp = L.DomUtil.create('button', 'kart-knapp reg-knapp');
        knapp.textContent = '➕ Marker punkt';
        knapp.title = 'Registrer et feltpunkt (bare synlig for deg)';
        L.DomEvent.disableClickPropagation(knapp);
        L.DomEvent.on(knapp, 'click', function () {
          if (beholder.classList.contains('reg-modus')) avsluttModus(); else startModus();
        });
        return knapp;
      }
    });
    new Knapp().addTo(m);

    // Langt trykk (mobil) eller høyreklikk (PC) markerer direkte der du trykker.
    m.on('contextmenu', function (e) { apneSkjema(e.latlng.lat, e.latlng.lng, null); });

    // Lenke fra adminpanelet: #...&punkt=lat,lon zoomer til punktet.
    // Lasteren tar vare på hashen før dashbordet skriver den om (window._regLenke).
    var treff = /(?:^|[#&])punkt=(-?[\d.]+),(-?[\d.]+)/.exec(window._regLenke || location.hash);
    if (treff) {
      var ll = [parseFloat(treff[1]), parseFloat(treff[2])];
      setTimeout(function () { m.setView(ll, 17); L.popup().setLatLng(ll).setContent('📍 Feltpunkt').openOn(m); }, 800);
    }

    visPunkter(null);
    hentFil().then(function (f) { visPunkter(f.liste); }).catch(function () { /* vises ved neste sending */ });
    sendKo();
  }

  // Kartet lages etter at siden er lastet: vent på det.
  var vent = setInterval(function () {
    var m = g('map');
    if (m && window.L) { clearInterval(vent); init(m); }
  }, 300);
})();
