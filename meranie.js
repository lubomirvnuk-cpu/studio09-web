/* Studio09 — meranie kontaktov pre Google reklamu (konverzie) a súhlas s cookie.
   Kým návštevník nesúhlasí, Google nedostane žiadne cookie (režim súhlasu, všetko „denied“).
   Počíta sa: klik na WhatsApp, klik na telefónne číslo, odoslaný formulár.
   Kódy konverzií sú z účtu Google Ads 248-922-4074 (Ciele → Konverzie). */
(function () {
  var AW = 'AW-18566690934';
  var KONVERZIE = {
    whatsapp: AW + '/brRFCMTqhbodEPbwpJVF',
    telefon: AW + '/xJbRCMfqhbodEPbwpJVF',
    formular: AW + '/YEezCKK_yLUdEPbwpJVF'
  };
  var KLUC = 's09_cookies';

  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  function citaj() { try { return JSON.parse(localStorage.getItem(KLUC) || 'null'); } catch (e) { return null; } }
  function stav(a, m) {
    return { ad_storage: m ? 'granted' : 'denied', ad_user_data: m ? 'granted' : 'denied',
      ad_personalization: m ? 'granted' : 'denied', analytics_storage: a ? 'granted' : 'denied' };
  }
  var ulozene = citaj();
  var predvolene = stav(false, false); predvolene.wait_for_update = 500;
  gtag('consent', 'default', predvolene);
  if (ulozene) gtag('consent', 'update', stav(ulozene.analyticke, ulozene.marketing));
  gtag('set', 'ads_data_redaction', true);
  gtag('set', 'url_passthrough', true);
  gtag('js', new Date());
  gtag('config', AW);
  var s = document.createElement('script'); s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + AW;
  document.head.appendChild(s);

  /* súhlas — volá ho lišta na titulke aj lišta nižšie */
  window.s09Suhlas = function (a, m) {
    try { localStorage.setItem(KLUC, JSON.stringify({ nutne: 1, analyticke: a ? 1 : 0, marketing: m ? 1 : 0, kedy: Date.now() })); } catch (e) {}
    gtag('consent', 'update', stav(a, m));
  };

  /* konverzia — volá sa po odoslaní formulára; WhatsApp a telefón sa počítajú samé */
  window.s09Konverzia = function (typ) {
    if (KONVERZIE[typ]) gtag('event', 'conversion', { send_to: KONVERZIE[typ], value: 1.0, currency: 'EUR' });
  };
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var h = a.getAttribute('href') || '';
    if (h.indexOf('wa.me/') > -1 || h.indexOf('whatsapp.com') > -1) window.s09Konverzia('whatsapp');
    else if (h.indexOf('tel:') === 0) window.s09Konverzia('telefon');
  }, true);

  /* lišta so súhlasom na podstránkach (titulka má vlastnú) */
  function lista() {
    if (citaj() || document.getElementById('cookie')) return;
    var st = document.createElement('style');
    st.textContent = '.s09c{position:fixed;left:0;right:0;bottom:0;z-index:300;display:flex;justify-content:center;padding:14px}' +
      '.s09c>div{width:100%;max-width:560px;background:rgba(11,15,26,.96);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);' +
      'border:1px solid rgba(237,241,248,.16);padding:20px 22px;box-shadow:0 24px 60px -14px rgba(0,0,0,.8);color:#EDF1F8}' +
      '.s09c h4{font:800 15px Archivo,sans-serif;text-transform:uppercase;letter-spacing:-.01em;margin:0 0 8px}' +
      '.s09c p{font:400 13px/1.6 Inter,sans-serif;color:#AFBDD6;margin:0}' +
      '.s09c p a{color:#1CF0C0}' +
      '.s09c .b{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}' +
      '.s09c button{padding:11px 18px;border:1.5px solid #1CF0C0;background:transparent;color:#1CF0C0;cursor:pointer;' +
      'font:700 11px Archivo,sans-serif;letter-spacing:.12em;text-transform:uppercase}' +
      '.s09c button.m{background:#1CF0C0;color:#0D1220}' +
      '@media(max-width:700px){.s09c{padding:8px;bottom:calc(76px + env(safe-area-inset-bottom,0px))}.s09c>div{padding:16px}}';
    document.head.appendChild(st);
    var d = document.createElement('div'); d.className = 's09c';
    d.innerHTML = '<div><h4>Súbory cookie</h4><p>Nevyhnutné cookie potrebujeme na fungovanie stránky. Marketingové slúžia na meranie, či funguje naša reklama. ' +
      '<a href="/#cookies">Viac o cookie</a></p><div class="b"><button class="m" data-v="1">Prijať všetko</button><button data-v="0">Len nevyhnutné</button></div></div>';
    d.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      var ano = b.getAttribute('data-v') === '1'; window.s09Suhlas(ano, ano); d.remove();
    });
    document.body.appendChild(d);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', lista); else lista();
})();
