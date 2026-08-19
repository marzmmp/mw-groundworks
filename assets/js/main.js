/* ==========================================================================
   M&W GroundWorks — site behaviour
   Motion follows the UI/UX Pro Max motion.csv specs (scroll-reveal: 300-400ms
   power1.out, y-offset 8-16px; stagger: 0.02-0.04s per item) implemented
   natively so the site ships with zero third-party runtime.
   ========================================================================== */
(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------------------- nav */
  var burger = document.querySelector('.burger');
  var links = document.getElementById('nav-links');
  if (burger && links) {
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') === 'true';
      burger.setAttribute('aria-expanded', String(!open));
      links.classList.toggle('open', !open);
    });
    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        burger.setAttribute('aria-expanded', 'false');
        links.classList.remove('open');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && links.classList.contains('open')) {
        burger.setAttribute('aria-expanded', 'false');
        links.classList.remove('open');
        burger.focus();
      }
    });
  }

  /* ------------------------------------------------------------- reveal
     IntersectionObserver is the primary trigger, but it can miss entries
     during fast or programmatic scrolling — and a missed entry would leave
     content invisible forever. A rect-based sweep on scroll plus a hard
     failsafe guarantee everything is revealed no matter what. */
  var rv = Array.prototype.slice.call(document.querySelectorAll('[data-rv]'));
  function show(el) {
    if (el.classList.contains('in')) return;
    var i = parseInt(el.getAttribute('data-rv'), 10) || 0;
    el.style.transitionDelay = Math.min(i * 0.035, 0.28) + 's';
    el.classList.add('in');
  }
  function showAll() { rv.forEach(show); rv = []; }

  if (reduce || !('IntersectionObserver' in window)) {
    showAll();
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        show(e.target);
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.01 });
    rv.forEach(function (el) { io.observe(el); });

    /* Synchronous, timestamp-throttled. Deliberately not rAF-scheduled: the
       hero's WebGL loop saturates the frame budget, which both delays
       IntersectionObserver delivery (its callbacks coalesce to the *final*
       scroll position, so fast scrolls skip elements) and would starve a
       rAF-based sweep. The work here is a shrinking array of rect reads. */
    var last = 0;
    var sweep = function () {
      var now = Date.now();
      if (now - last < 40) return;
      last = now;
      var vh = window.innerHeight || 0;
      rv = rv.filter(function (el) {
        if (el.classList.contains('in')) return false;
        var r = el.getBoundingClientRect();
        if (r.top < vh * 0.94) { show(el); io.unobserve(el); return false; }
        return true;
      });
      if (!rv.length) {
        window.removeEventListener('scroll', sweep);
        window.removeEventListener('resize', sweep);
      }
    };
    window.addEventListener('scroll', sweep, { passive: true });
    window.addEventListener('resize', sweep, { passive: true });
    sweep();
    // failsafe: nothing stays hidden past 6s regardless of what went wrong
    window.setTimeout(showAll, 6000);
  }

  /* --------------------------------------------------- before / after */
  document.querySelectorAll('.ba').forEach(function (ba) {
    var range = ba.querySelector('input[type=range]');
    if (!range) return;
    function set(v) { ba.style.setProperty('--pos', v + '%'); }
    set(range.value);
    range.addEventListener('input', function () { set(range.value); });
  });

  /* ------------------------------------------------- multi-step quote */
  document.querySelectorAll('form[data-steps]').forEach(function (form) {
    var steps = Array.prototype.slice.call(form.querySelectorAll('.qstep'));
    var bar = form.querySelector('.qbar');
    var count = form.querySelector('.qcount');
    var done = form.querySelector('.qdone');
    var i = 0;

    if (bar) {
      steps.forEach(function () {
        var b = document.createElement('i');
        bar.appendChild(b);
      });
    }

    function paint() {
      steps.forEach(function (s, n) { s.classList.toggle('on', n === i); });
      if (bar) Array.prototype.forEach.call(bar.children, function (b, n) {
        b.classList.toggle('on', n <= i);
      });
      if (count) count.textContent = 'Step ' + (i + 1) + ' of ' + steps.length;
      var h = steps[i].querySelector('legend');
      if (h) { steps[i].setAttribute('tabindex', '-1'); steps[i].focus({ preventScroll: true }); }
    }

    function valid(step) {
      var ok = true;
      step.querySelectorAll('[data-req]').forEach(function (f) {
        var e = step.querySelector('[data-err="' + f.getAttribute('data-req') + '"]');
        var good;
        if (f.type === 'radio' || f.type === 'checkbox') {
          good = !!step.querySelector('input[name="' + f.name + '"]:checked');
        } else {
          good = f.value.trim().length > 0;
          if (f.type === 'tel') good = good && f.value.replace(/\D/g, '').length >= 10;
        }
        if (e) e.classList.toggle('on', !good);
        if (!good && ok) { ok = false; (f.focus && f.type !== 'radio') && f.focus(); }
      });
      return ok;
    }

    form.querySelectorAll('[data-next]').forEach(function (b) {
      b.addEventListener('click', function () {
        if (!valid(steps[i])) return;
        if (i < steps.length - 1) { i++; paint(); }
      });
    });
    form.querySelectorAll('[data-prev]').forEach(function (b) {
      b.addEventListener('click', function () { if (i > 0) { i--; paint(); } });
    });

    function succeed() {
      steps.forEach(function (s) { s.classList.remove('on'); });
      if (bar) bar.style.display = 'none';
      if (count) count.style.display = 'none';
      if (done) { done.hidden = false; done.setAttribute('tabindex', '-1'); done.focus(); }
    }

    /* Last resort: hand the lead to the visitor's mail client, pre-filled.
       Losing a job because a Worker was down is unacceptable for a business
       whose whole pitch is "we call you back the same day". */
    function mailFallback(data, to, biz) {
      var body = Object.keys(data).map(function (k) {
        return k.replace(/^\w/, function (c) { return c.toUpperCase(); }) + ': ' + data[k];
      }).join('\n');
      var href = 'mailto:' + to
        + '?subject=' + encodeURIComponent('Estimate request — ' + (data.need || 'general'))
        + '&body=' + encodeURIComponent(body + '\n\n— sent from the ' + biz + ' website');
      window.location.href = href;
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!valid(steps[i])) return;

      // Bots fill every field they can see, including the one nobody can.
      var hp = form.querySelector('[data-honeypot]');
      if (hp && hp.value) { succeed(); return; }

      var btn = form.querySelector('[type=submit]');
      var label = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }

      var data = {};
      new FormData(form).forEach(function (v, k) { if (k !== 'company') data[k] = v; });
      data.page = window.location.pathname;

      var endpoint = form.getAttribute('data-endpoint');
      var to = form.getAttribute('data-mailto');
      var biz = form.getAttribute('data-biz') || 'the';

      if (!endpoint) {
        // No backend configured. Do NOT show a success state — an unsent form
        // that says "Request sent" is worse than no form at all.
        if (btn) { btn.disabled = false; btn.textContent = label; }
        mailFallback(data, to, biz);
        return;
      }

      var ctl = new AbortController();
      var timer = window.setTimeout(function () { ctl.abort(); }, 9000);

      window.fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        signal: ctl.signal
      }).then(function (r) {
        window.clearTimeout(timer);
        if (!r.ok) throw new Error('HTTP ' + r.status);
        succeed();
      }).catch(function () {
        window.clearTimeout(timer);
        if (btn) { btn.disabled = false; btn.textContent = label; }
        mailFallback(data, to, biz);
      });
    });

    paint();
  });

  /* ------------------------------------------------------------ year */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  /* ---------------------------------------------- nav active + shadow */
  var nav = document.querySelector('.nav');
  if (nav) {
    var onScroll = function () {
      nav.style.boxShadow = window.scrollY > 12
        ? '0 8px 32px rgba(0,0,0,.55)' : 'none';
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }
})();
