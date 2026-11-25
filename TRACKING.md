# Analytics

Sent by `shared/cgd-embed.js` to `https://www.cgdev.org` as `type: 'cgd_analytics'`.
`interactive_view` fires once on load. Engagement events:

| interactive_name | action_type | action_label | action_value |
|---|---|---|---|
| `adaptation-gap-2026-f1-flows` | `filter` | `recipient_group` | `all`, `ldc`, `sids` |
| | `view_control` | `series_toggle` | `public_hidden`, `public_shown`, `private_hidden`, `private_shown` |
| | `view_control` | `fullscreen` | none |
| `adaptation-gap-2026-f2-gap` | `filter` | `recipient_group` | `all`, `ldcsids` |
| | `filter` | `flow_scenario` | `trip24`, `tripdbl`, `uncond` |
| | `view_control` | `fullscreen` | none |
| `adaptation-gap-2026-f3-instruments` | `filter` | `recipient_group` | `income`, `vuln` |
| | `view_control` | `measure` | `share`, `usd` |
| | `view_control` | `instrument_toggle` | `<grant\|conc\|nonconc\|other>_<hidden\|shown>` |
| | `view_control` | `fullscreen` | none |

Hover, tooltips, resize and scroll are not tracked.
