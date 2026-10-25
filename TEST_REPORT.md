# Version 2 verification report

Date: 2026-10-25. This report distinguishes completed checks from pending verification.

## Completed locally

- **8/8 pytest tests passed**, including deterministic rebuilds, null preservation, field-map coverage, percentages, ranks, exclusions and exact population parity.
- **867 towns**; all town GUIDs match between SAPS and F1015. Aggregate `IE0` excluded and documented. Zero unmatched towns.
- **No complete category partition discrepancies** in `data/category_checks.json`.
- Independently executed `pipeline/fetch.py`: all four downloads succeeded and matched committed SHA-256 checksums exactly.
- Static build completed; `web/dist/index.html` exists. JavaScript syntax check passed.
- **8/8 Chromium Playwright tests passed**: desktop 1440×1000 and mobile 360×780. Search/dropdown, alphabetical ordering, keyboard operation, all fields/sections, rank/state population share, deep links, explicit fetch failure and invalid-town recovery passed.
- axe WCAG A/AA scans returned **zero violations** in both Chromium viewports. No browser console/page errors on successful loads; no horizontal overflow.
- Mobile full-page screenshot inspected.
- Full [Ballycotton sanity log](data/BALLYCOTTON_SANITY.md) generated. Diagnostic differences remain visible; no newspaper figure is used in application output.

## Local environment limitation

WebKit downloaded successfully but cannot launch because the host lacks required GTK/GStreamer and related libraries. `npx playwright install-deps chromium webkit` failed due to host process/permission constraints. WebKit tests are **not locally verified**. The committed CI uses `ubuntu-latest` and `npx playwright install --with-deps chromium webkit`; both WebKit projects are required before deployment. Tests are never skipped to allow a deployment.

The Playwright configuration and test files use CommonJS to avoid an observed ESM test-loader hang in this host’s Node 24 runtime. Application code remains an ES module. Playwright is pinned to 1.56.1 for reproducible browser revisions; CI uses Node 22.

## GitHub Actions: all tests passed; publication blocked by Pages setup

[Verified workflow run](https://github.com/seekq/towns/actions/runs/40220066461), source commit `a4cb82b38d60a0bb5584763d7676a836876bab8a`:

- **8/8 pytest tests passed** in GitHub’s Python 3.11 environment.
- **16/16 Playwright tests passed** in 28.1 seconds: Chromium desktop, Chromium mobile, WebKit desktop, WebKit mobile.
- Every browser/viewport passed the axe scan with zero violations, no unexpected console/page errors, and no horizontal overflow.
- Static build and the Ballycotton diagnostic passed. The full report and source-data artifact is available from the run’s **verification-and-data** artifact.
- The source tree was checked against the local implementation and matched exactly (`41ba015165926cf22747dc22f3e4bed7d994170c`).

The overall workflow is marked failed **only because `actions/configure-pages@v5` could not find a Pages site**. Its error was: “Please verify that the repository has Pages enabled and configured to build using GitHub Actions.” The deploy job was skipped. No application test failed.

### Exact deployment handoff

1. Open https://github.com/seekq/towns/settings/pages .
2. Under **Build and deployment → Source**, select **GitHub Actions**.
3. Open https://github.com/seekq/towns/actions/workflows/pages.yml and choose **Run workflow** on `main`, leaving data refresh off.
4. After both jobs pass, open the URL returned by the deploy job (expected https://seekq.github.io/towns/).

The connected GitHub tools support source commits and workflow inspection but do not expose Pages creation/settings. No authenticated browser settings change was attempted.

**Live-site verification: pending.** The deployment target returned HTTP 404 before Pages setup. It must not be described as live. The workflow includes a published-site HTML/JSON smoke test after deployment. The previous ChatGPT-hosted site is unaffected.
