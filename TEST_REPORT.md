# Version 2 verification report

Date: 2026-10-25. This report distinguishes completed checks from pending verification.

## Completed locally

- **8/8 pytest tests passed**, including deterministic rebuilds, null preservation, field-map coverage, percentages, ranks, exclusions and exact population parity.
- **867 towns**; all town GUIDs match between SAPS and F1015. Aggregate `IE0` excluded and documented. Zero unmatched towns.
- **No complete category partition discrepancies** in `data/category_checks.json`.
- Static build completed; `web/dist/index.html` exists. JavaScript syntax check passed.
- **8/8 Chromium Playwright tests passed**: desktop 1440×1000 and mobile 360×780. Search/dropdown, alphabetical ordering, keyboard operation, all fields/sections, rank/state population share, deep links, explicit fetch failure and invalid-town recovery passed.
- axe WCAG A/AA scans returned **zero violations** in both Chromium viewports. No browser console/page errors on successful loads; no horizontal overflow.
- Mobile full-page screenshot inspected.
- Full [Ballycotton sanity log](data/BALLYCOTTON_SANITY.md) generated. Diagnostic differences remain visible; no newspaper figure is used in application output.

## Local environment limitation

WebKit downloaded successfully but cannot launch because the host lacks required GTK/GStreamer and related libraries. `npx playwright install-deps chromium webkit` failed due to host process/permission constraints. WebKit tests are **not locally verified**. The committed CI uses `ubuntu-latest` and `npx playwright install --with-deps chromium webkit`; both WebKit projects are required before deployment. Tests are never skipped to allow a deployment.

The Playwright configuration and test files use CommonJS to avoid an observed ESM test-loader hang in this host’s Node 24 runtime. Application code remains an ES module. Playwright is pinned to 1.56.1 for reproducible browser revisions; CI uses Node 22.

## Deployment state

GitHub Pages target: https://seekq.github.io/towns/ . **Not yet verified live in this report.** The source workflow deploys only after all pipeline and Chromium/WebKit tests pass. Pages must be enabled with GitHub Actions as the repository’s Pages source. The previous ChatGPT-hosted site is unaffected.
