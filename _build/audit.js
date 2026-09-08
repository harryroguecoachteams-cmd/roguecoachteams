/* =============================================================================
   Responsive + contrast audit harness.

   Paste into the console on any page of this site (served over http, not
   file://), then:

       await audit.responsive();      // 72 probes, 6 pages x 12 widths
       await audit.contrast();        // every text node, WCAG AA

   Each probe loads a page into an offscreen iframe at a fixed width and
   measures the rendered DOM. It strips the `js` class first, which puts every
   reveal into its finished state instantly, so nothing is measured mid
   transition. Layout measurement is reliable even when the tab is occluded;
   TIMING is not, so never use this to test a transition.
   See the notes at the bottom.
   ========================================================================== */
window.audit = (function () {
  'use strict';

  var PAGES = ['index.html', 'about.html', 'services.html', 'sprint.html',
               'pricing.html', 'contact.html', 'insights.html',
               'coaching-scams.html',
               'authority-building-for-coaches.html',
               'joint-ventures-for-coaches.html'];
  var WIDTHS = [320, 375, 390, 430, 600, 768, 834, 1024, 1180, 1280, 1440, 1920];

  // decorative or deliberately off-canvas: the closed nav panel, the skip link.
  // Anything INSIDE the closed panel is off canvas by design too, so probe 2
  // also skips descendants of #nav rather than only the panel itself.
  var IGNORE = /^(drawer|skip)/;

  function frame(page, w, h) {
    return new Promise(function (resolve) {
      var f = document.createElement('iframe');
      f.style.cssText = 'position:fixed;left:-99999px;top:0;border:0;width:' +
                        w + 'px;height:' + (h || 900) + 'px';
      f.src = page;
      document.body.appendChild(f);
      var t = setTimeout(done, 3500);
      f.addEventListener('load', function () { clearTimeout(t); done(); }, { once: true });
      function done() {
        f.contentDocument.documentElement.classList.remove('js');
        setTimeout(function () { resolve(f); }, 120);
      }
    });
  }

  function lum(c) {
    var m = c.match(/[\d.]+/g).map(Number);
    function ch(v) { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }
    return 0.2126 * ch(m[0]) + 0.7152 * ch(m[1]) + 0.0722 * ch(m[2]);
  }
  function ratio(a, b) {
    var x = lum(a), y = lum(b);
    return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
  }

  async function responsive(pages, widths) {
    pages = pages || PAGES; widths = widths || WIDTHS;
    var out = [], t0 = performance.now();
    for (var i = 0; i < pages.length; i++) {
      for (var j = 0; j < widths.length; j++) {
        var f = await frame(pages[i], widths[j]);
        var d = f.contentDocument, w = f.contentWindow, de = d.documentElement;
        var r = { p: pages[i].replace('.html', ''), w: widths[j] };

        // 1. does the document scroll sideways
        r.ov = de.scrollWidth - de.clientWidth;

        // 2. anything sticking out past the edges that is not decorative
        r.wide = [].slice.call(d.querySelectorAll('body *'))
          .filter(function (e) { return !e.closest('#nav'); })
          .map(function (e) {
          var b = e.getBoundingClientRect();
          return { c: (e.getAttribute('class') || e.tagName).slice(0, 26),
                   r: Math.round(b.right), l: Math.round(b.left) };
        }).filter(function (o) {
          return (o.r > de.clientWidth + 1 || o.l < -1) && !IGNORE.test(o.c) && o.c !== 'A';
        }).slice(0, 5);

        // 3. a masked headline line wider than its own mask is INVISIBLE, not
        //    overflowing, so this never shows up as a scrollbar
        r.clip = [].slice.call(d.querySelectorAll('.ln')).map(function (ln) {
          var i2 = ln.firstElementChild;
          return { t: i2.textContent.slice(0, 22),
                   need: Math.round(i2.scrollWidth), have: Math.round(ln.clientWidth) };
        }).filter(function (o) { return o.need > o.have + 1; });

        // 4. WCAG 2.2 target size, ignoring the off-canvas nav panel
        r.small = [].slice.call(d.querySelectorAll('a,button,input,select,textarea'))
          .filter(function (e) { return e.tabIndex !== -1 && !e.classList.contains('skip') && !e.closest('#nav'); })
          .map(function (e) {
            var b = e.getBoundingClientRect();
            return { t: (e.textContent || e.getAttribute('aria-label') || e.type || '').trim().slice(0, 18),
                     w: Math.round(b.width), h: Math.round(b.height) };
          }).filter(function (o) { return o.w > 0 && o.h > 0 && (o.w < 24 || o.h < 24); });

        // 5. micro type. The audience is women 40+ on a phone.
        r.tiny = [].slice.call(d.querySelectorAll('p,li,dd,figcaption,span,label,h4,a,button'))
          .filter(function (e) {
            return parseFloat(w.getComputedStyle(e).fontSize) < 12.1 &&
                   e.textContent.trim().length > 3 && e.offsetParent;
          }).map(function (e) {
            return (e.getAttribute('class') || e.tagName) + ':' +
                   Math.round(parseFloat(w.getComputedStyle(e).fontSize) * 10) / 10;
          });
        r.tiny = r.tiny.filter(function (v, k, a) { return a.indexOf(v) === k; });

        f.remove();
        out.push(r);
      }
    }
    return report(out, Math.round(performance.now() - t0));
  }

  function report(out, ms) {
    var agg = { ov: {}, clip: {}, small: {}, tiny: {}, wide: {} };
    out.forEach(function (r) {
      if (r.ov > 0) { agg.ov[r.p + '@' + r.w] = r.ov; }
      r.clip.forEach(function (c) { agg.clip[c.t + '@' + r.w] = c.need + '>' + c.have; });
      r.small.forEach(function (s) { agg.small[s.t + ' ' + s.w + 'x' + s.h] = 1; });
      r.tiny.forEach(function (t) { agg.tiny[t] = 1; });
      r.wide.forEach(function (x) { agg.wide[x.c + '@' + r.w] = x.r; });
    });
    var clean = !Object.keys(agg.ov).length && !Object.keys(agg.clip).length &&
                !Object.keys(agg.small).length;
    console.log('%c' + out.length + ' probes in ' + ms + 'ms: ' +
                (clean ? 'CLEAN' : 'FAILURES'),
                'font-weight:bold;color:' + (clean ? '#1F3D33' : '#C9694A'));
    console.log(agg);
    return agg;
  }

  async function contrast(pages, width) {
    pages = pages || PAGES;
    var fails = {}, n = 0;
    for (var i = 0; i < pages.length; i++) {
      var f = await frame(pages[i], width || 1280);
      var d = f.contentDocument, w = f.contentWindow;
      var nodes = [].slice.call(d.querySelectorAll('body *')).filter(function (e) {
        if (!e.offsetParent && w.getComputedStyle(e).position !== 'fixed') { return false; }
        return [].some.call(e.childNodes, function (t) {
          return t.nodeType === 3 && t.textContent.trim().length > 1;
        });
      });
      n += nodes.length;
      nodes.forEach(function (e) {
        var cs = w.getComputedStyle(e), fg = cs.color, p = e, bg = 'rgba(0, 0, 0, 0)';
        while (p && p !== d.documentElement) {
          var b = w.getComputedStyle(p).backgroundColor;
          if (b && !/rgba\(0, 0, 0, 0\)|transparent/.test(b)) { bg = b; break; }
          p = p.parentElement;
        }
        if (bg === 'rgba(0, 0, 0, 0)') { bg = 'rgb(255, 255, 255)'; }
        if (/rgba/.test(bg) && !/, 1\)$/.test(bg)) { return; }   // translucent, skip
        var fs = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight, 10) >= 700;
        var need = (fs >= 24 || (fs >= 18.66 && bold)) ? 3 : 4.5;
        var got = ratio(fg, bg);
        if (got < need) {
          fails[(e.getAttribute('class') || e.tagName).slice(0, 26) + '|' + fg + '|' + bg] =
            (e.getAttribute('class') || e.tagName).slice(0, 26) + ' "' +
            e.textContent.trim().slice(0, 20) + '" ' + fs + 'px  ' + fg + ' on ' + bg +
            '  ' + (Math.round(got * 100) / 100) + '/' + need;
        }
      });
      f.remove();
    }
    var list = Object.keys(fails).map(function (k) { return fails[k]; });
    console.log('%c' + n + ' text nodes: ' + (list.length ? list.length + ' FAILURES' : 'zero failures'),
                'font-weight:bold;color:' + (list.length ? '#C9694A' : '#1F3D33'));
    list.forEach(function (l) { console.log('  ' + l); });
    return list;
  }

  return { responsive: responsive, contrast: contrast, PAGES: PAGES, WIDTHS: WIDTHS };
})();

/* -----------------------------------------------------------------------------
   Notes, so this does not get misused.

   * Serve over http. Chrome blocks file:// for this, and a single-threaded
     python http.server serialises ~20 asset requests into an 18 second page
     load, which makes every probe unusable. Use ThreadingTCPServer.

   * Stripping the `js` class is what makes this fast and honest: every hidden
     state in style.css is scoped to html.js, so removing it lands the whole
     page in its finished state with no waiting and no transitions in flight.

   * Layout is trustworthy here. Timing is not. An occluded Chrome window
     reports document.timeline.currentTime === 0 and every CSS transition reads
     as stuck at its start value, and an offscreen iframe has the same problem.
     To check what a transition RESOLVES to, set el.style.transition='none',
     read the computed style, then restore. To check that it actually runs, use
     a real click and a screenshot.

   * `wide` entries are informational. An element can extend past the edge and
     be harmless if a parent clips it; `ov` is the number that decides whether
     the page really scrolls sideways.
   -------------------------------------------------------------------------- */
