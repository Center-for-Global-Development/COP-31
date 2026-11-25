/* =============================================================================
   Project helpers for the AGR 2026 figure set. Loaded after dom.js and
   chart-core.js. Everything here is shared by all three figures so a fix made
   once applies to the whole set. Exposes window.AGR.
   ============================================================================= */
(() => {
  const { element } = window.CGDDom;
  const { trimZeros } = window.CGDCore;

  /* One source line, identical on every figure of the set. */
  const SOURCE = 'Source: CGD analysis of UNEP, Adaptation Gap Report 2026.';

  /* US$ billions. One decimal place by default; `digits` 0 for the 2035 view,
     whose source values are whole numbers. A real value never shows as zero. */
  function usd(v, digits = 1) {
    if (!Number.isFinite(v)) return 'N/A';
    const small = 10 ** -digits;
    if (v > 0 && v < small / 2) return `<US$${small}bn`;
    return `US$${trimZeros(v.toFixed(digits))}bn`;
  }
  function pct(fraction) {
    if (!Number.isFinite(fraction)) return 'N/A';
    return `${Math.round(fraction * 100)}%`;
  }

  /* ONE notes paragraph: source, then lines true of the current state, then
     lines true whatever is selected (references/02 §2.8). */
  function renderNotes(host, { visible = [], notes = [] } = {}) {
    const text = [SOURCE, ...visible, ...notes].filter(Boolean).join(' ');
    host.replaceChildren(document.createTextNode(text));
  }

  /* Segmented control: buttons carry data-value; calls onChange(value). */
  function segmented(id, onChange) {
    const group = document.getElementById(id);
    group.addEventListener('click', e => {
      const btn = e.target.closest('button[data-value]');
      if (!btn || btn.getAttribute('aria-pressed') === 'true') return;
      group.querySelectorAll('button[data-value]').forEach(b =>
        b.setAttribute('aria-pressed', String(b === btn)));
      onChange(btn.dataset.value);
    });
  }

  /* Clickable categorical legend (show/hide), references/10 §10.7.
     items: [{key, label, colour, tip, toggle}] ; hidden: Set of keys. */
  function legend(host, items, hidden, onToggle) {
    host.replaceChildren(...items.map(it => {
      const swatch = element('span', { className: 'swatch' + (it.swatchClass ? ' ' + it.swatchClass : '') });
      swatch.style.setProperty('--swatch', it.colour);
      if (it.toggle === false) {
        const span = element('span', { className: 'legend-item legend-static' }, [swatch, document.createTextNode(it.label)]);
        if (it.tip) span.setAttribute('data-tip', it.tip);
        return span;
      }
      const off = hidden.has(it.key);
      const btn = element('button', {
        className: 'legend-item' + (off ? ' muted' : ''),
        attributes: { type: 'button', 'aria-pressed': String(!off), 'data-key': it.key,
                      'data-tip': it.tip || (off ? `Show ${it.label.toLowerCase()}` : `Hide ${it.label.toLowerCase()}`) }
      }, [swatch, document.createTextNode(it.label)]);
      btn.addEventListener('click', () => {
        // Never allow every series to be hidden: the chart would look broken.
        const toggleable = items.filter(i => i.toggle !== false).map(i => i.key);
        if (!off && toggleable.filter(k => !hidden.has(k)).length <= 1) return;
        onToggle(it.key, !off);
      });
      return btn;
    }));
  }

  /* Tooltip: immediate on hover and keyboard focus; tap pins it on touch;
     Escape or a tap elsewhere closes it (references/10 §10.9). */
  const tooltip = () => document.getElementById('tooltip');
  let pinned = null;
  function place(cx, cy) {
    const tip = tooltip(), pad = 10, box = tip.getBoundingClientRect();
    const vw = document.documentElement.clientWidth, vh = document.documentElement.clientHeight;
    let top = cy - box.height - 12;
    if (top < pad) top = cy + 16;
    const left = Math.max(pad, Math.min(cx - box.width / 2, vw - box.width - pad));
    tip.style.left = left + 'px';
    tip.style.top = Math.max(pad, Math.min(top, vh - box.height - pad)) + 'px';
  }
  function showTip(title, rows, cx, cy) {
    const tip = tooltip();
    const grid = element('div', { className: 'tooltip-grid' });
    rows.forEach(([k, v]) => grid.append(element('span', { text: k }), element('b', { text: v })));
    tip.replaceChildren(element('strong', { text: title }), ...(rows.length ? [grid] : []));
    const host = document.fullscreenElement || document.getElementById('vizRoot');
    if (tip.parentNode !== host) host.append(tip);
    tip.hidden = false;
    place(cx, cy);
  }
  function hideTip() { const t = tooltip(); if (t) t.hidden = true; pinned = null; }
  function attachTip(node, content) {
    const open = (x, y) => { const c = content(); showTip(c.title, c.rows, x, y); };
    node.addEventListener('pointerenter', e => {
      if (e.pointerType === 'touch') return;
      const b = node.getBoundingClientRect(); open(e.clientX, b.top);
    });
    node.addEventListener('pointermove', e => {
      if (e.pointerType === 'touch' || tooltip().hidden) return;
      place(e.clientX, node.getBoundingClientRect().top);
    });
    node.addEventListener('pointerleave', e => { if (e.pointerType !== 'touch' && !pinned) hideTip(); });
    node.addEventListener('click', e => {
      const b = node.getBoundingClientRect();
      if (pinned === node) { hideTip(); return; }
      open(e.clientX || b.left + b.width / 2, b.top); pinned = node;
      e.stopPropagation();
    });
    node.addEventListener('focus', () => { const b = node.getBoundingClientRect(); open(b.left + b.width / 2, b.top); });
    node.addEventListener('blur', () => { if (pinned !== node) hideTip(); });
    node.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); node.dispatchEvent(new MouseEvent('click')); } });
  }
  document.addEventListener('keydown', e => { if (e.key === 'Escape') hideTip(); });
  document.addEventListener('click', e => { if (pinned && !pinned.contains(e.target)) hideTip(); });
  document.addEventListener('scroll', hideTip, true);

  function wireFullscreen() {
    const btn = document.getElementById('fullscreenBtn');
    if (!btn) return;
    btn.addEventListener('click', () => {
      const root = document.getElementById('vizRoot');
      if (document.fullscreenElement === root) document.exitFullscreen();
      else root.requestFullscreen?.();
    });
  }

  /* "Nice" axis maximum and ticks for a value domain starting at zero. */
  function niceTicks(max, target) {
    const raw = max / Math.max(1, target);
    const mag = 10 ** Math.floor(Math.log10(raw));
    const step = [1, 2, 2.5, 5, 10].map(s => s * mag).find(s => s >= raw);
    const top = Math.ceil(max / step) * step;
    const ticks = [];
    for (let v = 0; v <= top + step / 1000; v += step) ticks.push(+v.toFixed(6));
    return { top, ticks, step };
  }

  window.AGR = { SOURCE, usd, pct, renderNotes, segmented, legend, attachTip, hideTip, wireFullscreen, niceTicks };
})();
