# Irish Towns Census Explorer — version 2

A static, responsive Census 2022 snapshot of **867 Irish towns**, built only from official Central Statistics Office (CSO) downloads. Search by town or county, select a town, and explore population, age, people, work, families, homes and services. Deep links use `?town=<CSO GUID>`.

**GitHub Pages deployment target:** https://seekq.github.io/towns/ — publication is blocked until Pages is enabled in repository settings. All 8 pipeline and 16 browser tests passed in [GitHub Actions](https://github.com/seekq/towns/actions/runs/40220066461). Details and the exact handoff are recorded in [TEST_REPORT.md](TEST_REPORT.md).

Version 2 intentionally uses **Census 2022 only**, as specified. It replaces the web experience with a static app that requires no server, CSO API proxy or key. The Python CLI remains available; see [version 1 CLI documentation](docs/VERSION_1.md). The previous ChatGPT-hosted Worker and its identity are retained for history; committing this static app does not update that older URL.

## Install, rebuild and run

Requires Python **3.11+**, Node.js **22+**, and npm.

```sh
git clone https://github.com/seekq/towns.git
cd towns
npm ci
python -m pip install pytest

# One command: re-download all official inputs and rebuild towns.json + sanity log
npm run rebuild:data

# Rebuild using committed raw inputs; no CSO network dependency
python pipeline/build.py

# Package static folder with index.html at its root
npm run build
python -m http.server 8080 --directory web/dist
```

Open http://localhost:8080. For an iPhone, open the deployed URL in Safari and use **Share → Add to Home Screen**. This is a static web app, not an App Store application. No personal information is collected. Internet access is needed to load it; no service worker or offline guarantee is supplied.

A download error stops the refresh with the failing URL. Files are all downloaded before replacing inputs; no sample or synthetic fallback exists. Each rebuild verifies SHA-256 checksums and the current glossary descriptions. If official definitions change, review the field map rather than bypassing the error.

## Sources and geography

- [SAPS Census 2022 source page](https://www.cso.ie/en/census/census2022/census2022smallareapopulationstatistics/): towns/built-up-area CSV and the revised XLSX glossary.
- [F1015](https://data.cso.ie/table/F1015): authoritative names, county labels and population, selected for Census 2022 and both sexes.
- [FY001](https://data.cso.ie/table/FY001): national population, Census 2022, State, both sexes.
- [Download URLs, dates and checksums](data/raw/SOURCES.md), with machine-readable manifest in `data/raw/sources.json`.

The town-file aggregate labelled “State”/“Ireland” (`IE0`) is the **built-up-area population aggregate**, not the national population. It is excluded as a non-town in [exclusions.json](data/exclusions.json). The national denominator is read from FY001. Never sum towns to infer the population of Ireland.

Join SAPS `GUID` to F1015 `C04160V04929`, never names. All 867 town GUIDs match; `data/unmatched.json` records any failures and the build stops if there are any. The SAPS CSV is Windows-1252; the pipeline decodes it explicitly and writes UTF-8 output. Names are retained exactly from F1015, including accents and capitalization. Multi-county labels are retained. Towns share competition ranks when populations tie (1, 2, 2, 4).

## Field map and definitions

Every requested field has an entry in [field_map.json](data/field_map.json), including source columns, exact glossary descriptions, denominator column/description and interpretation notes. [Readable mapping table](data/FIELD_MAP_REVIEW.md).

| Section | Source / denominator |
| --- | --- |
| Population and age | T1_1 / total population |
| Marital status | T1_2 / published all-age marital-status total |
| Irish language | T3_1 / population aged 3+ |
| Citizenship | T2_1 citizenship categories / citizenship total |
| Religion | T2_4 / religion total |
| General health | T12_3 / general health total |
| Carers and disability | T12_2 and T12_1 counts / total population |
| Economic status | T8_1 / persons aged 15+ |
| Remote work | T11_1 work-at/from-home / work commuting base |
| Families | T4_3 one-parent totals / T4_1 total families |
| Single-person households | T5_1 / private household total |
| Housing | T6 tables / each table’s own household or dwelling total |
| Internet and cars | T15 / each question’s household total |

Approved semantic adjustments: marital status is all ages, “Irish” means citizenship (not native-born), unemployed includes first-job seekers plus short- and long-term unemployed, carers/disability use total population, and “No smoke alarms” uses the CSO label. Group/private water sums group schemes with public source, group schemes with private source, and other private sources. The terminal `GE5BRH` bedroom band is displayed as 5+; the glossary abbreviates its description to “5 bedrooms.”

Explicit sums use source categories only: ages 0–4 and 75+, non-Irish citizenship categories, one-parent mothers/fathers, unemployment categories, group/private water, and three-plus cars. Rental types are shown separately. No field is calculated by subtraction. “Other religion” uses the CSO aggregate directly. Civil partnerships are included in the CSO married category and cannot be separated.

### Fields shown as n/a

| Field | Reason |
| --- | --- |
| Daily smokers | SAPS publishes all smokers combined, without a daily-only category. |
| Married couples without children (families) | Published family tables do not identify married vs cohabiting couples. Household composition is a different measure. |
| Married couples with children (families) | Same limitation; no substitution with household counts. |
| Cohabiting couples (families) | Same limitation; no matching family-type row. |

Blank/suppressed source cells stay null, including any aggregate whose component is null. Zero remains zero. Percentages require a known count and a positive denominator. A true zero denominator has no defined percentage and displays n/a.

## Tests

```sh
python -m pytest tests/pipeline -q
python pipeline/sanity.py
npm run build
npx playwright install --with-deps chromium webkit
npm run test:e2e
```

Pipeline tests cover population parity, town coverage/exclusions, unique IDs, rank ties, nonnegative data, percentage arithmetic, complete category partitions, mapping coverage, null parsing, glossary consistency and deterministic rebuilds. Source partition results are in `data/category_checks.json`; no discrepancy tolerance is silently applied.

Playwright runs Chromium and WebKit at desktop and **360px mobile** widths. It checks all options and sorting, keyboard search, selection, deep links, every field and section, header figures, error handling, console errors, horizontal overflow and axe WCAG A/AA findings. Reports are saved under `playwright-report/` and `test-results/` (not checked in); CI uploads them as an artifact. See [test report](TEST_REPORT.md).

[Ballycotton sanity log](data/BALLYCOTTON_SANITY.md) compares every supplied newspaper figure and marks differences over 10%. It never supplies application data or asserts newspaper parity. Differences may reflect definition, measure or boundary; their cause is not assumed. Notably, bedroom household counts differ from the newspaper, and daily-only smoking cannot be compared.

## GitHub Pages

The committed workflow `.github/workflows/pages.yml` runs on each push to `main`: builds data from committed raw files, runs pytest, builds static output, runs all Playwright projects, and deploys **only after checks pass**. `web/dist` is the deployment artifact.

For first-time setup, open **Repository Settings → Pages → Build and deployment → Source → GitHub Actions**. Then run **Actions → Test and deploy Census Explorer → Run workflow**. The workflow cannot deploy if Pages is disabled or repository policies block it. The `github-pages` environment may also require approval under your repository settings.

The CSO fetch runs **only** on manual workflow dispatch when **Refresh official inputs** is selected. The refreshed sources and manifest are uploaded with the verification artifact; they are not silently pushed back to `main`. Download and review them, or run `npm run rebuild:data` locally and commit the inputs/output, to make the refresh durable in Git. Push-triggered CI always uses the committed raw files.

After deployment, the workflow smoke-tests the published HTML and JSON. For a full browser smoke test against a deployed site:

```sh
TEST_BASE_URL=https://seekq.github.io/towns/ npm run test:e2e
```

### Manual free-hosting alternative

Run `npm run build`, then drag the **web/dist folder** (containing `index.html` at its root) onto https://app.netlify.com/drop. Upload the folder, not the repository or a lone HTML file. Netlify supplies the public URL; account and retention terms are set by Netlify.

## Layout

- `pipeline/`: fetch, glossary parser, builder, newspaper sanity diagnostic.
- `data/raw/`: original downloads, source URLs/dates/checksums.
- `data/`: field map, exclusions, unmatched report, partitions and sanity log.
- `web/`: static HTML, CSS, JS, data and static builder. `worker/` is retained version 1 source.
- `tests/pipeline/`, `tests/e2e/`: pytest and Playwright tests.
- `.github/workflows/pages.yml`: gated build, verification and Pages deployment.

## Attribution and licence

Source: **Central Statistics Office, Ireland, Census 2022 SAPS, F1015 and FY001**, downloaded on the date in the source manifest. CSO statistical information is licensed under **Creative Commons Attribution 4.0 (CC BY 4.0)**; see [CSO Copyright and Re-use Policy](https://www.cso.ie/en/aboutus/whoweare/copyrightpolicy/) and [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The app selects and sums identified published categories and computes percentages/ranks; it is not a CSO product or endorsement. Preserve this attribution when redistributing data. No newspaper artwork is reproduced. No separate open-source licence has been assigned to the application code.
