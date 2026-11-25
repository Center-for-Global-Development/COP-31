# Adaptation Gap Report 2026: interactive figures

Three embeddable CGD figures built from UNEP's *Adaptation Gap Report 2026: Ready? Not.*
(main report and appendices, November 2026). They show adaptation finance needs and
flows at group level; the report does not publish per-country needs or flows.

| File | Question it answers | Default state | Controls |
|---|---|---|---|
| `f1-flows-2019-2024.html` | How have adaptation flows moved since 2019, against the Glasgow doubling target? | All developing countries | Recipients (all / LDCs / SIDS); legend toggles public vs mobilised private |
| `f2-finance-gap-2035.html` | How much of 2035 needs would tripled flows meet? | All developing countries; triple the 2025 doubling | Recipients (all / LDCs and SIDS); flow scenario |
| `f3-instruments-2024.html` | Who gets grants and who gets loans? | Income groups; shares | Recipients (income groups / LDCs and SIDS); measure (share / US$); legend toggles instruments |

`preview.html` embeds all three the way cgdev.org does (review only, not for publication).

## Embedding

```html
<iframe src="https://center-for-global-development.github.io/COP-31/f1-flows-2019-2024.html"
  title="Bar chart: international adaptation finance to developing countries, LDCs and SIDS, 2019 to 2024"
  loading="lazy" scrolling="no" style="display:block;width:100%;height:560px;border:0"></iframe>
```

Height is set by the `cgd-iframe-resize` message from `shared/cgd-embed.js`.

## Data

All values are typed in from the report and listed with their source in
`data/agr2026-figures.csv`. Each was checked against the rendered PDF page, not only
extracted text:

* f1: main report figure 2.3a (all developing countries) and figure 2.4 (LDCs, SIDS);
  2024 LDC and SIDS values also match appendix table 2.C.5.
* f2: figures 2.7 and 2.8. Gaps are computed in the figure (needs minus flows) and
  reproduce the report's printed gaps: 335 / 300 / 231 and 36 / 27 / 12.
* f3: figure 2.5. Income-group totals match appendix table 2.C.4 (5.6, 12.5, 5.3, 0.1).

Hand-checked benchmarks: 2024 flows US$31.4bn (28.2 public + 3.2 private); tripling the
doubling meets 120/420 = 29% of 2035 needs; low-income grant share 4.1/5.6 = 73%.

## Settled design calls

* **Mixed price bases in f1.** Bars are constant 2024 US$; the doubling targets are
  nominal, as the Glasgow Climate Pact and the report define them. Stated in the notes.
* **"~40" target label** for all developing countries: the report gives "approximately
  US$40 billion".
* **Printed totals.** Where the report prints a total that differs from the sum of its
  rounded parts by 0.1 (e.g. 2019: 25.0 vs 25.1; LDCs 2024: 10.2 vs 10.3), labels show
  the printed total. Shares in f3 use the sum of the parts so bars reach 100%.
* **f2 legend is static.** The flow layers are cumulative scenarios chosen with the
  scenario control, so a show/hide legend would duplicate that control.
* **LDCs and SIDS are combined in f2** because the report gives needs only for the
  combined group.

## Dependencies

None beyond the CGD shared layer in `shared/` (`cgd-embed.js`, `cgd-figure.css`,
`cgd-responsive.css`, `chart-core.js`, `dom.js`, copied unchanged) plus this set's
`shared/agr.js` and `shared/agr.css`. No CDN scripts.

## QA

```powershell
python qa/verify.py      # SKILL §F audits at 320/768/1200px
python qa/exercise.py    # every control state, tooltips on hover and tap, height grow/shrink
python qa/shots.py       # screenshots to qa/shots/
```

Bump the `?v=` stamp on every asset link (and in `preview.html`) with each change.
Current stamp: `20261125a`.
