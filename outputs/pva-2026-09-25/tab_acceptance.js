// Tab acceptance, measured in a REAL browser (paste into the devtools console on a served review page, at desktop width and
// again at a phone width). Acceptance: after clicking each tab, THAT tab's own heading (h3.tabname) is visible and fully inside
// the first viewport. Three scenarios: from the top of the page; from the tab bar after having scrolled to the bottom of the
// previous tab; and a click while scrolled deep (the button off-screen). A heading that is hidden counts as a FAIL, never as
// "top = 0" (a hidden element reports a zero rectangle -- the first version of this check passed 11/11 on the broken page
// for exactly that reason).
(async function () {
  const accept = async function (scenario) {
    const res = [], nav = document.querySelector('nav'), tabs = [...document.querySelectorAll('nav button')];
    for (let i = 0; i < tabs.length; i++) {
      const b = tabs[i];
      if (scenario === 'top') scrollTo(0, 0);
      else {
        tabs[(i + tabs.length - 1) % tabs.length].click(); await new Promise(r => setTimeout(r, 100));
        scrollTo(0, document.body.scrollHeight); await new Promise(r => setTimeout(r, 50));
        if (scenario === 'from-navbar') scrollTo(0, nav.getBoundingClientRect().top + scrollY);
      }
      b.click(); await new Promise(r => setTimeout(r, 150));
      const h = document.getElementById('tab-' + b.dataset.t).querySelector('h3.tabname');
      const vis = !!h && getComputedStyle(h).display !== 'none' && h.getBoundingClientRect().height > 0;
      const top = vis ? Math.round(h.getBoundingClientRect().top) : null;
      res.push({tab: b.dataset.t, top, ok: vis && top >= 0 && top + h.getBoundingClientRect().height <= innerHeight});
    }
    return {scenario, vw: innerWidth, vh: innerHeight, pass: res.filter(x => x.ok).length, of: res.length,
            fails: res.filter(x => !x.ok).map(x => x.tab + '@' + x.top)};
  };
  const out = [await accept('top'), await accept('from-navbar'), await accept('deep-programmatic')];
  out.push({above_tabs_px: Math.round(document.querySelector('nav').getBoundingClientRect().top + scrollY)});
  console.log(JSON.stringify(out, null, 1));
  return out;
})();
