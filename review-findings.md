## REVIEW CLEAN — All P0 and P1 fixed
## Multi-Persona Review: asa.html (Asa v2.0.0)
### Date: 2026-03-25
### Summary: 6 P0 [ALL FIXED], 11 P1 [ALL FIXED], 14 P2 (deferred)
### Test suite: 85/85 pass

---

#### P0 -- Critical (must fix before submission)

- **P0-1** [FIXED] [Statistical]: GRIM rounding check uses 3-point sampling instead of interval check, producing false positives. Example: `mean=3.53, n=17, decimals=2` — true sum interval [59.925, 60.095] contains integer 60, but all 3 test points miss it. Since GRIM FAIL = SWALLOWED (Tier A), this is a false conviction. (line ~507)
  - Fix: Replace 3-point check with interval check: `Math.floor((mean+halfUnit)*effectiveN + 1e-9) >= Math.ceil((mean-halfUnit)*effectiveN - 1e-9)`

- **P0-2** [FIXED] [Security]: XSS via unescaped study names in innerHTML across all render functions. `r.study` from user CSV inserted raw in renderGauntlet (~1503), renderHeatmap (~1639), renderReports (~1697), duplication table (~1575). A CSV with `<img src=x onerror=alert(1)>` as study name executes JS.
  - Fix: Apply `escapeAttr()` to all user-derived strings before innerHTML insertion.

- **P0-3** [FIXED] [Security]: XSS via unescaped CSV column headers in mapping preview (~1192) and data preview table (~1164).
  - Fix: Wrap `parsed.headers[idx]` and row values with `escapeAttr()`.

- **P0-4** [FIXED] [Domain]: About tab says "Five are per-study" but only lists 4 (GRIM, SPRITE, statcheck, GRIMMER). Claims "5 per-study + 3 dataset-level = 7" but 4+3=7. The text contradicts itself. (~line 139, 143)
  - Fix: Change to "Four are per-study (GRIM, SPRITE, statcheck, GRIMMER) and three are dataset-level"

- **P0-5** [FIXED] [Domain]: SPRITE classified as Tier A "conclusive impossibility" but it's a stochastic search — failure after 10K iterations ≠ proof of impossibility. Only exhaustive enumeration would be conclusive. (~line 1386)
  - Fix: Downgrade SPRITE to Tier B ("strong evidence") or add explicit caveat that SPRITE FAIL = "highly implausible" not "mathematically impossible"

- **P0-6** [FIXED] [Engineering]: CSV parser breaks on quoted fields containing commas. `parseCSV()` uses naive `split(sep)`, so `"Smith, J 2020"` becomes two columns, corrupting all downstream analysis. (~line 1017)
  - Fix: Implement RFC 4180-aware CSV parsing that respects quoted fields.

#### P1 -- Important (should fix)

- **P1-1** [FIXED] [Security]: CSV formula injection in exports. Study names starting with `=`, `+`, `@` can be interpreted as formulas by Excel. Neither Clean CSV nor Flagged CSV sanitize. (~line 1808-1825)
  - Fix: Prepend `'` to cell values starting with `=+@\t\r`.

- **P1-2** [FIXED] [Statistical]: GRIMMER doesn't account for mean rounding — only varies SD by ±halfUnit while holding mean fixed. Can produce false positives similar to P0-1. (~line 572)
  - Fix: When GRIM passes via rounding (mean ≠ exact), pass the actual valid mean (nearest integer sum / n) to GRIMMER.

- **P1-3** [FIXED] [Statistical]: Benford's Law minimum sample too low (30). At n=30, expected count for digit 9 is only 1.37, well below the chi-squared >=5 rule. (~line 865)
  - Fix: Raise minimum to 100, or document as a known limitation.

- **P1-4** [FIXED] [Domain]: Duplication threshold (4/6 fields) lacks empirical justification. No false-positive rate analysis. Two RCTs measuring the same biomarker with similar sample sizes could match by chance. (~line 917)
  - Fix: Add a note that this is exploratory. Consider adding a Bonferroni-corrected p-value or permutation test.

- **P1-5** [FIXED] [Domain]: Fujii demo dataset uses fabricated data attributed to a real person. Could be seen as creating fictional evidence. (~line 1100-1113)
  - Fix: Use actual retracted Fujii data with citation, or use clearly fictional author names.

- **P1-6** [FIXED] [Engineering]: `crypto.subtle` unavailable over plain `file://` in Chrome. `sha256hex()` promise rejects silently, receipt stays "Generating..." forever. No `.catch()`. (~line 1751-1782)
  - Fix: Add `.catch()` fallback (e.g., simple hash or "Hash unavailable" message).

- **P1-7** [FIXED] [Engineering]: Study names with commas break CSV export. `[r.study, ...].join(',')` produces malformed CSV. (~line 1811)
  - Fix: Quote all CSV fields properly (wrap in `"`, escape internal `"`).

- **P1-8** [FIXED] [UX]: No keyboard Escape handler for settings modal + no focus trap + no focus management. Keyboard users trapped. (~line 314)
  - Fix: Add Escape key listener, focus trap, and focus return on close.

- **P1-9** [FIXED] [UX]: Tabs lack ARIA wiring (`aria-controls`, `aria-labelledby`) and arrow key navigation per WAI-ARIA tabs pattern. (~line 88-127, 288)
  - Fix: Add proper ARIA attributes and arrow key handlers with roving tabindex.

- **P1-10** [FIXED] [UX]: No visible focus indicators (`:focus-visible`) anywhere. Keyboard users can't see what's focused. (~line 23)
  - Fix: Add global `.btn:focus-visible, .tab-btn:focus-visible, input:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }`

- **P1-11** [FIXED] [Domain]: statcheck reference should cite Nuijten et al. (2016) *Behavior Research Methods* for the method, not just the R package. (~line 199)
  - Fix: Update citation.

#### P2 -- Minor (nice to fix)

- **P2-1** [Statistical]: TDA About tab says ">=20 values" but code requires >=50. Documentation mismatch. (~line 205 vs 797)
- **P2-2** [Statistical]: xoshiro128** uses s[0] not s[1] for result — non-standard variant. No practical impact. (~line 597)
- **P2-3** [Statistical]: Terminal digit extraction loses trailing zeros (`String(3.10)` → `"3.1"`). Systematic bias against digit 0. (~line 784)
- **P2-4** [Engineering]: Version comment says "v1.0.0" but code is v2.0.0. Stale comment. (~line 281)
- **P2-5** [Engineering]: `qnorm()` function defined but never called. Dead code. (~line 448)
- **P2-6** [Engineering]: `heatCell()` accepts `study` and `fang` params but never uses them. Dead parameters. (~line 1600)
- **P2-7** [Domain]: Fang numbering skips 4 in the Gauntlet table header (shows "1, 2, 3, 5"). Non-sequential. (~line 1488)
- **P2-8** [Domain]: GRIMMER tolerance of 0.01 is generous — original Anaya (2016) uses stricter. Could mask failures at large n. (~line 568)
- **P2-9** [Domain]: About tab says "swap-based optimization" for SPRITE but code uses random generation. Documentation mismatch. (~line 236)
- **P2-10** [Domain]: Mosimann et al. year wrong in code comment (2002 vs correct 1995). (~line 779)
- **P2-11** [Domain]: statcheck decision error 0.001 dead-zone not documented. Deviation from original statcheck. (~line 759)
- **P2-12** [UX]: Report accordion cards not keyboard-accessible (no role="button", no tabindex, no Enter/Space). (~line 1695)
- **P2-13** [UX]: Arabic verse text lacks `lang="ar"` attribute. Screen readers misread. (~line 79, 129)
- **P2-14** [UX]: Badge contrast borderline: green #2ea043 on dark bg-card ~4.2:1, below AA for 12px. (~line 54)

#### False Positive Watch
- escapeAttr() handles &, ", ', <, > — safe for both attribute and text content escaping
- DOR = exp(mu1 + mu2) IS correct (not relevant here but in lessons.md)
- Div balance verified: 95/95
- Blob URL cleanup is correct (revokeObjectURL called immediately)
- No ReDoS patterns found
- No prototype pollution found
