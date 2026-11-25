#!/usr/bin/env python
"""Screenshot every figure at the review widths, in each control state.

  python qa/shots.py

Writes qa/shots/<figure>-<state>-<width>.png (git-ignored).
"""
from __future__ import annotations
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import serve, REPO  # noqa: E402

OUT = REPO / "qa" / "shots"
WIDTHS = [320, 390, 700, 1200]
CLICK = "(sel) => document.querySelector(sel).click()"
STATES = {
    "f1-flows-2019-2024.html": {
        "all": None,
        "ldc": "#groupToggle [data-value=ldc]",
        "sids": "#groupToggle [data-value=sids]",
    },
    "f2-finance-gap-2035.html": {
        "all": None,
        "ldcsids": "#groupToggle [data-value=ldcsids]",
    },
    "f3-instruments-2024.html": {
        "income": None,
        "usd": "#measureToggle [data-value=usd]",
        "vuln": "#compareToggle [data-value=vuln]",
    },
    "f4-flows-to-2035.html": {
        "all": None,
        "ldcsids": "ldcsids",
        "ldc": "ldc",
        "sids": "sids",
    },
}
SELECT = ("(v) => { const s = document.getElementById('groupSelect');"
          " s.value = v; s.dispatchEvent(new Event('change')); }")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with serve(REPO) as port, sync_playwright() as pw:
        browser = pw.chromium.launch()
        for fig, states in STATES.items():
            for label, sel in states.items():
                for w in WIDTHS:
                    page = browser.new_page(viewport={"width": w, "height": 900})
                    page.goto(f"http://127.0.0.1:{port}/{fig}", wait_until="load")
                    page.wait_for_function("() => window.CGD_READY === true", timeout=15000)
                    if sel and sel.startswith("#"):
                        page.evaluate(CLICK, sel)
                    elif sel:
                        page.evaluate(SELECT, sel)
                    page.wait_for_timeout(300)
                    path = OUT / f"{fig[:2]}-{label}-{w}.png"
                    page.screenshot(path=str(path), full_page=True)
                    page.close()
                    print(path.name)
        browser.close()


if __name__ == "__main__":
    main()
