# Irish Towns — CSO Ireland explorer

**Deployed app:** https://cso-towns-phone.tq49qqc5nn.chatgpt.site

Explore official Irish statistics through a Python command-line tool or an iPhone-friendly web app. Both use CSO Ireland's public PxStat API; no CSO API key is required.

## Web app

The web app provides:

- Town and county-name search against the Census 2022 town list.
- Population, average age and age-group summaries, plus statistics by sex.
- A browser for CSO subjects, collections and tables, with a value selector for each dimension.
- CSV download of all returned cells; the on-screen table displays up to 200 cells.
- A responsive interface that can be added to an iPhone Home Screen.

The deployed ChatGPT Site is private to its owner and may request ChatGPT sign-in. Open the URL in Safari, tap **Share → Add to Home Screen**, and choose **Add**. It is a Home Screen web app, rather than an App Store/native iOS application. Internet access is required; there is no offline data cache. Census figures refer to 2022, not today's population.

## Repository files

| Path | Purpose |
| --- | --- |
| `cso.py` | Python CLI |
| `requirements.txt` | CLI dependencies |
| `tests/test_cso.py` | CLI regression tests |
| `web/worker/index.js` | Web interface and server-side CSO proxy, embedded in one Worker module |
| `web/scripts/build.sh` | Package the Worker into `web/dist/` |
| `web/scripts/validate-artifact.mjs` | Validate the built Worker and hosting manifest |
| `web/.openai/hosting.json` | Identity of the existing ChatGPT Site |
| `web/wrangler.jsonc` | Configuration for optional Cloudflare Workers hosting |

## Install and run the CLI

Requires Python 3.9 or later. On macOS or Linux:

```sh
git clone https://github.com/seekq/towns.git
cd towns
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 cso.py --help
```

For later sessions, enter the repository directory and activate `.venv` again. The CLI does not require a web server.

## CLI commands

The general syntax is:

```text
python3 cso.py [--lang LANGUAGE] COMMAND [ARGUMENTS] [OPTIONS]
```

`--lang` defaults to `en` and must appear before the command. CSO must supply the requested table in that language. Use `--help` for global help or `COMMAND --help` for command-specific help.

| Command | Arguments | Purpose / options |
| --- | --- | --- |
| `subjects` | None | List subjects; `--contains TEXT` filters their names. |
| `products` | `SUBJECT` | List collections in a subject; `--contains TEXT` filters names. |
| `tables` | `SUBJECT PRODUCT` | List tables; `--contains TEXT` filters names. |
| `meta` | `SUBJECT PRODUCT TABLE` | Show dimensions; `--show-values` lists category codes and labels. |
| `values` | `SUBJECT PRODUCT TABLE` | Find category codes; `--dimension CODE_OR_NAME` selects a dimension and `--contains TEXT` searches codes and labels. |
| `data` | `SUBJECT PRODUCT TABLE` | Query data; options are listed below. |

### Data options

| Option | Meaning |
| --- | --- |
| `--select 'CODE=V1,V2'` | Select category codes or labels; repeat for different dimensions. |
| `--select 'CODE=*'` | Select all values in that dimension. Omitted dimensions also select all. |
| `--format FORMAT` | `json-stat2` (default), `json-stat`, `csv`, `xlsx`, or `px`. |
| `--output FILE` | Save the complete API response. Required for CSV, XLSX and PX. JSON formats also display a table. |
| `--max-rows N` | Limit displayed cells; default 200, positive integers only. Does not truncate the saved response. |
| `--codes` | Display category codes instead of labels for JSON formats. |
| `--pivot CODE` | Pivot dimension for native CSV/XLSX exports only. |
| `--pyjstat-hint` | Legacy compatibility flag; accepted but currently has no effect. pandas/pyjstat are not required. |

A dimension can be specified by code or exact dimension name. A value can be a category code, an exact label, or a unique label fragment, matched without case sensitivity. Ambiguous matches and unknown values are rejected. Values are separated by commas, so use a code or unique fragment when a label itself contains a comma. Specify a dimension once and combine its values in that selection.

### Example: Lisdoonvarna population

Discover the table and its codes:

```sh
python3 cso.py subjects --contains census
python3 cso.py products 76
python3 cso.py tables 76 C2022P1 --contains population
python3 cso.py meta 76 C2022P1 F1015
python3 cso.py values 76 C2022P1 F1015 --contains Lisdoonvarna
```

Query population using the town name:

```sh
python3 cso.py data 76 C2022P1 F1015 \
  --select 'List of Towns=Lisdoonvarna' \
  --select 'STATISTIC=F1015C01'
```

The verified Census 2022 response is 934 people: 385 male and 549 female. To return only the total:

```sh
python3 cso.py data 76 C2022P1 F1015 \
  --select 'List of Towns=Lisdoonvarna' \
  --select 'STATISTIC=F1015C01' \
  --select 'C02199V02655=Both sexes'
```

Save all statistics for the town:

```sh
python3 cso.py data 76 C2022P1 F1015 \
  --select 'List of Towns=Lisdoonvarna' \
  --format csv --output lisdoonvarna.csv
```

Save the complete JSON-stat 2 response while displaying only three cells:

```sh
python3 cso.py data 76 C2022P1 F1015 \
  --select 'List of Towns=Lisdoonvarna' \
  --output lisdoonvarna.json --max-rows 3
```

## Run and package the website

The web version is JavaScript, not a Python server. Its Worker serves the page, manifest and icon, and forwards validated queries to CSO. It needs a Worker-compatible server; serving the HTML alone through GitHub Pages will not provide its `/api` endpoint.

Requires Node.js 22 or later, npm and bash. Build and validate without installing dependencies:

```sh
cd web
npm run build
npm run validate
```

The build creates `dist/server/index.js` and `dist/.openai/hosting.json`. Edit `worker/index.js`, then rebuild; generated `dist/` files are not the source of truth. The HTML, CSS and client JavaScript are embedded in the module's `page` string.

Create a deployment archive from the generated output:

```sh
tar -czf ../irish-towns-site.tar.gz -C dist .
```

### Update the existing ChatGPT Site

The live Site URL is https://cso-towns-phone.tq49qqc5nn.chatgpt.site.

From ChatGPT Work with Sites connected, ask it to update this existing Site using the `web/` source in this repository. The existing identity is retained in `web/.openai/hosting.json`; do not create a second Site or substitute a new project ID.

The Sites publishing workflow must synchronize source to the Site's managed repository, build and validate the exact source commit, package `dist/`, save that version and deploy it with the existing private audience. A GitHub commit alone does **not** update the live Site. Sites source credentials and publishing operations are provided by ChatGPT Work; the ordinary `tar` command does not publish or authenticate a deployment.

### Optional: run locally or publish to your own Cloudflare Workers account

These commands use Cloudflare's official Wrangler CLI and the included `wrangler.jsonc`. They are an alternative hosting route; they do not update the existing ChatGPT Site.

From `web/`:

```sh
# Preview locally; open the localhost URL printed by Wrangler.
npx wrangler@4 dev

# Authenticate to your Cloudflare account and deploy.
npx wrangler@4 login
npx wrangler@4 deploy
```

Wrangler bundles `worker/index.js` directly, so the Sites archive is not needed for this route. Deployment prints the resulting website URL. This optional deployment is public by default and does not include ChatGPT's owner-only sign-in. No Cloudflare deployment was performed as part of this update.

## Tests and verification

From the repository root:

```sh
python3 -m unittest discover -s tests -v
```

The CLI was checked against live CSO metadata, JSON-stat 1 and 2, a Lisdoonvarna population query, and native CSV export. Its tests cover sparse values, category ordering, status flags, validation and retry exhaustion. Native XLSX/PX exports have not been live-tested. Web syntax, Worker artifact structure, proxy validation and cube parsing were checked; iPhone browser testing remains unverified.

## Troubleshooting

- **Missing requests/rich:** activate `.venv` and rerun `python3 -m pip install -r requirements.txt`.
- **Unknown dimension:** use `meta`; `TOWN` is not the dimension code for F1015. Use `C04160V04929` or `List of Towns`.
- **Unknown/ambiguous town:** use `values --contains NAME` and select the returned code.
- **Too much data:** add dimension filters. `--max-rows` reduces display only, not the download.
- **CSO unavailable:** try again later. The CLI retries transient failures and respects bounded `Retry-After` delays; the web app displays an error and allows another attempt.
- **Website returns old results:** table metadata may be cached for five minutes. Requests require internet access.

## References

- [CSO PxStat user guide](https://www.cso.ie/en/databases/userguides/pxstatuserguide/)
- [JSON-stat specification](https://json-stat.org/format/)
- [Wrangler configuration](https://developers.cloudflare.com/workers/wrangler/configuration/)
- [Wrangler Worker commands](https://developers.cloudflare.com/workers/wrangler/commands/workers/)
