#!/usr/bin/env python
"""Exercise state in each figure: every control value, legend toggles, tooltips
on real pointer events and taps, and iframe grow/shrink via preview.html.

  python qa/exercise.py
"""
from __future__ import annotations
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import serve, REPO, IN_PAGE_AUDIT  # noqa: E402

FAILS: list[str] = []
def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok: FAILS.append(msg)

def tip_on_hover(page, sel, label, touch=False):
    page.evaluate("() => { const t=document.getElementById('tooltip'); t.hidden=true; }")
    box = page.locator(sel).first.bounding_box()
    if touch:
        page.locator(sel).first.dispatch_event('click')
    else:
        page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] - 4)
    page.wait_for_timeout(80)
    vis = page.evaluate("() => !document.getElementById('tooltip').hidden && document.getElementById('tooltip').textContent")
    check(bool(vis), f"{label}: tooltip opens ({'tap' if touch else 'hover'}) -> {str(vis)[:60]!r}")

def audit(page, label, width):
    r = page.evaluate(IN_PAGE_AUDIT, width)
    check(not r['failures'], f"{label} @ {width}: audit {r['failures'] or 'clean'}")

with serve(REPO) as port, sync_playwright() as pw:
    b = pw.chromium.launch()
    base = f"http://127.0.0.1:{port}/"
    for width in (320, 1200):
        errors = []
        p = b.new_page(viewport={"width": width, "height": 900})
        p.on("pageerror", lambda e: errors.append(str(e)))
        p.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

        p.goto(base + "f1-flows-2019-2024.html"); p.wait_for_function("window.CGD_READY===true")
        tip_on_hover(p, "#chartWrap g.hit", "f1 bar")
        tip_on_hover(p, "#chartWrap g.hit >> nth=6", "f1 target", touch=True)
        p.click("#legend button[data-key=private]")
        n = p.evaluate("() => document.querySelectorAll('#chartWrap .seg-mark').length")
        check(n == 6, f"f1 hide private leaves 6 segments (got {n})")
        p.click("#legend button[data-key=public]")
        n = p.evaluate("() => document.querySelectorAll('#chartWrap .seg-mark').length")
        check(n == 6, f"f1 cannot hide the last series (got {n})")
        for v in ("ldc", "sids", "all"):
            p.click(f"#groupToggle [data-value={v}]"); p.wait_for_timeout(100)
            t = p.text_content("#vizTitle"); notes = p.text_content("#notes")
            check(notes.count("Source:") == 1, f"f1 {v}: one Source line; title={t!r}")
            n = p.evaluate("() => document.querySelectorAll('#chartWrap .seg-mark').length")
            check(n == (12 if v == "all" else 6), f"f1 {v}: private reset on group change ({n} segments)")
            audit(p, f"f1 {v}", width)

        p.goto(base + "f2-finance-gap-2035.html"); p.wait_for_function("window.CGD_READY===true")
        tip_on_hover(p, "#chartWrap g.hit", "f2 needs")
        tip_on_hover(p, "#chartWrap g.hit >> nth=2", "f2 flows segment", touch=True)
        for grp in ("all", "ldcsids"):
            p.click(f"#groupToggle [data-value={grp}]")
            for sc in ("trip24", "tripdbl", "uncond"):
                p.select_option("#scenarioSelect", sc); p.wait_for_timeout(60)
                gap = p.evaluate("() => [...document.querySelectorAll('.gap text')].map(t=>t.textContent).join(' | ')")
                print(f"      f2 {grp}/{sc}: {gap}")
            audit(p, f"f2 {grp}", width)

        p.goto(base + "f3-instruments-2024.html"); p.wait_for_function("window.CGD_READY===true")
        tip_on_hover(p, "#chartWrap g.hit", "f3 row")
        tip_on_hover(p, "#chartWrap g.hit >> nth=1", "f3 row", touch=True)
        for cmp in ("vuln", "income"):
            for ms in ("usd", "share"):
                p.click(f"#compareToggle [data-value={cmp}]"); p.click(f"#measureToggle [data-value={ms}]")
                p.wait_for_timeout(60)
                totals = p.evaluate("() => [...document.querySelectorAll('.bar-total')].map(t=>t.textContent).join(',')")
                print(f"      f3 {cmp}/{ms}: totals [{totals}] title={p.text_content('#vizTitle')!r}")
                audit(p, f"f3 {cmp}/{ms}", width)
        p.click("#legend button[data-key=grant]")
        check(p.evaluate("() => document.querySelector('#legend [data-key=grant]').getAttribute('aria-pressed')") == "false", "f3 grants hidden via legend")
        check(not errors, f"no console errors @ {width}: {errors[:3]}")
        p.close()

    # Iframe grow / shrink in the review page (resize contract is sent to
    # https://www.cgdev.org, so here we only confirm the body height changes
    # both ways; origin delivery is checked on the production parent).
    p = b.new_page(viewport={"width": 390, "height": 900})
    p.goto(base + "f2-finance-gap-2035.html"); p.wait_for_function("window.CGD_READY===true")
    h0 = p.evaluate("() => Math.ceil(document.body.getBoundingClientRect().height)")
    p.click("#groupToggle [data-value=ldcsids]"); p.wait_for_timeout(100)
    h1 = p.evaluate("() => Math.ceil(document.body.getBoundingClientRect().height)")
    p.click("#groupToggle [data-value=all]"); p.wait_for_timeout(100)
    h2 = p.evaluate("() => Math.ceil(document.body.getBoundingClientRect().height)")
    check(h1 != h0 and h2 == h0, f"f2 body height {h0} -> {h1} -> {h2} (grows and shrinks back)")
    b.close()

print(f"\n{'FAILED: ' + str(len(FAILS)) if FAILS else 'PASS: all state checks clean.'}")
sys.exit(1 if FAILS else 0)
