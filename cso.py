#!/usr/bin/env python3

"""

CSO Ireland PxStat CLI (PxAPIv1)

- List subjects/products/tables

- Fetch metadata (dimensions + codes)

- Query data (filtered) and display as a table

Spec: PxStat.Data.Cube_API.PxAPIv1 (official PxStat wiki)

"""

from __future__ import annotations

import argparse

import json

import sys

import time
import math
from pathlib import Path
from urllib.parse import quote
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

from dataclasses import dataclass

from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
    from rich.console import Console
    from rich.table import Table
except ImportError as exc:
    raise SystemExit("Install dependencies: python3 -m pip install requests rich") from exc

BASE = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.PxAPIv1"

DEFAULT_LANG = "en"

RETRY_STATUSES = {429, 500, 502, 503, 504}

DEFAULT_TIMEOUT = 30

console = Console(markup=False)

@dataclass(frozen=True)

class ApiPath:

    """PxAPIv1 path parts (subject/product/table)."""

    subject: Optional[str] = None

    product: Optional[str] = None

    table: Optional[str] = None

    pivot: Optional[str] = None

def _sleep_backoff(attempt: int) -> None:

    # 0.5, 1, 2, 4, 8 seconds (cap)

    delay = min(8.0, 0.5 * (2 ** attempt))

    time.sleep(delay)

def request_response(method, url, *, params=None, json_body=None,
                     timeout=DEFAULT_TIMEOUT, max_retries=6):
    """Retry read-only CSO queries, including throttling; preserve binary exports."""
    last_error = "No response"
    with requests.Session() as session:
        for attempt in range(max_retries):
            delay = min(8.0, 0.5 * (2 ** attempt))
            try:
                resp = session.request(method, url, params=params, json=json_body,
                                       timeout=timeout, headers={"Accept": "*/*"})
                if resp.status_code not in RETRY_STATUSES:
                    if not resp.ok:
                        raise SystemExit(f"HTTP {resp.status_code}: {resp.text[:1000]}")
                    return resp
                last_error = f"HTTP {resp.status_code}: {resp.text[:300]}"
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    try:
                        delay = max(0, float(retry_after))
                    except ValueError:
                        try:
                            delay = max(0, (parsedate_to_datetime(retry_after) -
                                            datetime.now(timezone.utc)).total_seconds())
                        except (ValueError, TypeError, OverflowError):
                            pass
                # Do not retry earlier than the server permits or hang for minutes.
                if delay > 60:
                    raise SystemExit(f"CSO asks you to retry after {delay:.0f} seconds. Try again later.")
            except (requests.Timeout, requests.ConnectionError) as exc:
                last_error = str(exc)
            if attempt + 1 < max_retries:
                time.sleep(delay)
    raise SystemExit(f"Failed after {max_retries} attempts: {url}\n{last_error}")


def request_json(method, url, **kwargs):
    resp = request_response(method, url, **kwargs)
    try:
        data = resp.json()
    except ValueError as exc:
        raise SystemExit(f"CSO returned invalid JSON: {resp.text[:300]}") from exc
    if isinstance(data, dict) and "error" in data:
        raise SystemExit(f"CSO API error: {data['error']}")
    return data


def pxapi_url(lang: str, path: ApiPath) -> str:

    parts = [BASE, lang]

    if path.subject is not None:

        parts.append(path.subject)

    if path.product is not None:

        parts.append(path.product)

    if path.table is not None:

        parts.append(path.table)

    if path.pivot is not None:

        parts.append(path.pivot)

    return "/".join([parts[0]] + [quote(str(part), safe="") for part in parts[1:]])

def print_id_text_list(items: List[Dict[str, Any]], title: str, limit: int = 200) -> None:

    tbl = Table(title=title)

    tbl.add_column("id", style="bold")

    tbl.add_column("text")

    tbl.add_column("type", justify="center")

    for i, it in enumerate(items[:limit]):

        tbl.add_row(str(it.get("id", "")), str(it.get("text", "")), str(it.get("type", "")))

    if len(items) > limit:

        tbl.caption = f"Showing {limit} of {len(items)}"

    console.print(tbl)

def cmd_subjects(args: argparse.Namespace) -> None:

    url = pxapi_url(args.lang, ApiPath())

    data = request_json("GET", url)

    if args.contains:

        needle = args.contains.lower()

        data = [d for d in data if needle in str(d.get("text", "")).lower()]

    print_id_text_list(data, f"CSO PxStat Subjects ({args.lang})")

def cmd_products(args: argparse.Namespace) -> None:

    url = pxapi_url(args.lang, ApiPath(subject=args.subject))

    data = request_json("GET", url)

    if args.contains:

        needle = args.contains.lower()

        data = [d for d in data if needle in str(d.get("text", "")).lower()]

    print_id_text_list(data, f"Products for Subject {args.subject} ({args.lang})")

def cmd_tables(args: argparse.Namespace) -> None:

    url = pxapi_url(args.lang, ApiPath(subject=args.subject, product=args.product))

    data = request_json("GET", url)

    if args.contains:

        needle = args.contains.lower()

        data = [d for d in data if needle in str(d.get("text", "")).lower()]

    print_id_text_list(data, f"Tables for {args.subject}/{args.product} ({args.lang})")

def cmd_meta(args: argparse.Namespace) -> None:

    url = pxapi_url(args.lang, ApiPath(subject=args.subject, product=args.product, table=args.table))

    meta = request_json("GET", url)

    console.print(f"Title: {meta.get('title','')}\n")

    tbl = Table(title="Variables (dimensions)")

    tbl.add_column("code", style="bold")

    tbl.add_column("text")

    tbl.add_column("#values", justify="right")

    for v in meta.get("variables", []):

        tbl.add_row(str(v.get("code","")), str(v.get("text","")), str(len(v.get("values", []) or [])))

    console.print(tbl)

    if args.show_values:

        for v in meta.get("variables", []):

            code = v.get("code","")

            text = v.get("text","")

            values = v.get("values", []) or []

            value_texts = v.get("valueTexts", []) or []

            console.print(f"\n{code} — {text}")

            vt = Table()

            vt.add_column("value", style="bold", overflow="fold")

            vt.add_column("valueText")

            for i in range(min(len(values), len(value_texts))):

                vt.add_row(str(values[i]), str(value_texts[i]))

            if len(values) != len(value_texts):

                # Some tables may omit valueTexts; still show raw values

                for val in values[len(value_texts):]:

                    vt.add_row(str(val), "")

            console.print(vt)

def parse_select(select_items: List[str]) -> List[Dict[str, Any]]:

    """

    Parse --select CODE=V1,V2 into PxAPI query objects:

    {"code": CODE, "selection": {"filter":"item","values":[V1,V2]}}

    """

    out: List[Dict[str, Any]] = []

    for item in select_items:

        if "=" not in item:

            raise SystemExit(f"Bad --select '{item}'. Use CODE=V1,V2 or CODE=*")

        code, raw = item.split("=", 1)

        code = code.strip()

        raw = raw.strip()
        if not code or not raw:
            raise SystemExit("A selection needs both a dimension and a value.")
        if any(q["code"] == code for q in out):
            raise SystemExit(f"Repeated selection for {code}; combine values with commas.")

        if raw == "*" or raw.lower() == "all":

            # PxAPIv1 generally interprets omission as "all". To be explicit, omit entirely.

            # So we just skip adding a filter for this dimension.

            continue

        vals = [v.strip() for v in raw.split(",") if v.strip()]

        out.append({"code": code, "selection": {"filter": "item", "values": vals}})

    return out

def resolve_select(items, meta):
    """Accept dimension codes/names and codes, exact labels or unique label fragments."""
    result = []
    used = set()
    for item in items:
        if "=" not in item:
            raise SystemExit(f"Bad selection {item!r}; use CODE=VALUE.")
        name, raw = (part.strip() for part in item.split("=", 1))
        candidates = [v for v in meta["variables"]
                      if name.casefold() in (v["code"].casefold(), v["text"].casefold())]
        if len(candidates) != 1:
            raise SystemExit(f"Unknown or ambiguous dimension {name!r}. Use the codes shown by meta.")
        var = candidates[0]
        if var["code"] in used:
            raise SystemExit(f"Repeated selection for {var['code']}.")
        used.add(var["code"])
        if raw.casefold() in ("*", "all"):
            continue
        values = []
        for value in raw.split(","):
            value = value.strip()
            if not value:
                raise SystemExit("Empty selection value.")
            if value in var["values"]:
                values.append(value)
                continue
            labels = var.get("valueTexts", var["values"])
            matches = [c for c, label in zip(var["values"], labels)
                       if label.casefold() == value.casefold()]
            if not matches:
                matches = [c for c, label in zip(var["values"], labels)
                           if value.casefold() in label.casefold()]
            if len(matches) != 1:
                raise SystemExit(f"Unknown or ambiguous value {value!r} for {var['code']}. "
                                 "Use the values command to find its code.")
            values.append(matches[0])
        result.append({"code": var["code"], "selection": {
            "filter": "item", "values": list(dict.fromkeys(values))}})
    return result


def normalize_dataset(data):
    """JSON-stat 2 root, JSON-stat 1 named dataset, or single-dataset array."""
    if isinstance(data, list):
        if len(data) != 1:
            raise ValueError("Expected one JSON-stat dataset.")
        data = data[0]
    if isinstance(data, dict) and "dimension" not in data:
        candidates = [v for v in data.values() if isinstance(v, dict) and "dimension" in v]
        if len(candidates) != 1:
            raise ValueError("Response does not contain one JSON-stat dataset.")
        data = candidates[0]
    if not isinstance(data, dict) or "dimension" not in data or "value" not in data:
        raise ValueError("Missing JSON-stat dimension/value fields.")
    dim = data["dimension"]
    ids = data.get("id", dim.get("id"))
    sizes = data.get("size", dim.get("size"))
    if not isinstance(ids, list) or not isinstance(sizes, list) or len(ids) != len(sizes):
        raise ValueError("Invalid dimension order or size.")
    if any(type(n) is not int or n < 1 for n in sizes):
        raise ValueError("Invalid dimension size.")
    info = []
    for name, size in zip(ids, sizes):
        d = dim[name]
        cat = d.get("category", {})
        index = cat.get("index")
        labels = cat.get("label", {})
        if isinstance(index, dict):
            if sorted(index.values()) != list(range(size)):
                raise ValueError(f"Invalid category positions for {name}.")
            keys = sorted(index, key=index.get)
        elif isinstance(index, list):
            keys = index
        elif size == 1 and len(labels) == 1:
            keys = list(labels)
        else:
            raise ValueError(f"Missing category index for {name}.")
        if len(keys) != size:
            raise ValueError(f"Category count mismatch for {name}.")
        info.append((name, keys, labels))
    total = math.prod(sizes)
    values = data["value"]
    if isinstance(values, list):
        if len(values) != total:
            raise ValueError("Value count does not match cube size.")
    elif isinstance(values, dict):
        if any(not str(k).isdigit() or not 0 <= int(k) < total for k in values):
            raise ValueError("Invalid sparse value index.")
    else:
        raise ValueError("Invalid values container.")
    return data, info, sizes, total


def iter_rows(dataset, info, sizes, total, codes=False):
    strides = [math.prod(sizes[i + 1:]) for i in range(len(sizes))]
    values = dataset["value"]
    status = dataset.get("status", {})
    for i in range(total):
        row = []
        for (_, keys, labels), stride, size in zip(info, strides, sizes):
            key = keys[(i // stride) % size]
            row.append(str(key if codes else labels.get(key, key)))
        value = values[i] if isinstance(values, list) else values.get(str(i))
        flag = (status[i] if i < len(status) else "") if isinstance(status, list) else (
            status.get(str(i), "") if isinstance(status, dict) else status)
        yield row + ["" if value is None else str(value), str(flag or "")]


def cmd_values(args):
    meta = request_json("GET", pxapi_url(args.lang, ApiPath(args.subject, args.product, args.table)))
    table = Table(title="Matching dimension values")
    for name in ("dimension", "dimension name", "value", "valueText"):
        table.add_column(name, overflow="fold")
    count = 0
    for var in meta.get("variables", []):
        if args.dimension and args.dimension.casefold() not in (var["code"].casefold(), var["text"].casefold()):
            continue
        for code, label in zip(var["values"], var.get("valueTexts", var["values"])):
            if args.contains and args.contains.casefold() not in (code + " " + label).casefold():
                continue
            count += 1
            table.add_row(var["code"], var["text"], code, label)
    table.caption = f"{count} matches"
    console.print(table)


def cmd_data(args):
    if args.max_rows < 1:
        raise SystemExit("--max-rows must be positive.")
    if args.format in ("csv", "xlsx", "px") and not args.output:
        raise SystemExit(f"--format {args.format} requires --output FILE.")
    if args.pivot and args.format not in ("csv", "xlsx"):
        raise SystemExit("--pivot is supported only for csv/xlsx.")
    path = ApiPath(args.subject, args.product, args.table)
    meta = request_json("GET", pxapi_url(args.lang, path))
    query = resolve_select(args.select or [], meta)
    url = pxapi_url(args.lang, ApiPath(args.subject, args.product, args.table, args.pivot))
    body = {"query": query, "response": {"format": args.format}}
    resp = request_response("POST", url, json_body=body)
    if args.format in ("csv", "xlsx", "px"):
        # The API may return an error as JSON even when a binary export was requested.
        if "json" in resp.headers.get("Content-Type", "").lower():
            raise SystemExit(f"Expected {args.format} export but received JSON: {resp.text[:500]}")
        if args.format == "xlsx" and not resp.content.startswith(b"PK"):
            raise SystemExit("CSO did not return a valid XLSX file.")
        Path(args.output).write_bytes(resp.content)
        console.print(f"Saved {args.output}")
        return
    try:
        data, info, sizes, total = normalize_dataset(resp.json())
    except (ValueError, KeyError, TypeError) as exc:
        raise SystemExit(f"Cannot parse CSO JSON-stat: {exc}") from exc
    if args.output:
        Path(args.output).write_text(json.dumps(resp.json(), ensure_ascii=False, indent=2), encoding="utf-8")
        console.print(f"Saved {args.output} (complete response)")
    table = Table(title=meta.get("title", args.table))
    for name, _, _ in info:
        table.add_column(name)
    table.add_column("value", justify="right")
    table.add_column("status")
    from itertools import islice
    for row in islice(iter_rows(data, info, sizes, total, args.codes), args.max_rows):
        table.add_row(*row)
    if total > args.max_rows:
        table.caption = f"Showing {args.max_rows} of {total} cells. Use --select to narrow results."
    console.print(table)


def build_parser() -> argparse.ArgumentParser:

    p = argparse.ArgumentParser(prog="cso.py", description="Query and display CSO PxStat data (PxAPIv1).")

    p.add_argument("--lang", default=DEFAULT_LANG)

    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("subjects", help="List subjects")

    s.add_argument("--contains", default=None)

    s.set_defaults(func=cmd_subjects)

    pr = sub.add_parser("products", help="List products for a subject id")

    pr.add_argument("subject")

    pr.add_argument("--contains", default=None)

    pr.set_defaults(func=cmd_products)

    t = sub.add_parser("tables", help="List tables for subject/product")

    t.add_argument("subject")

    t.add_argument("product")

    t.add_argument("--contains", default=None)

    t.set_defaults(func=cmd_tables)

    m = sub.add_parser("meta", help="Show metadata (dimensions + codes) for a table")

    m.add_argument("subject")

    m.add_argument("product")

    m.add_argument("table")

    m.add_argument("--show-values", action="store_true")

    m.set_defaults(func=cmd_meta)

    d = sub.add_parser("data", help="Query and display table data (filtered)")

    d.add_argument("subject")

    d.add_argument("product")

    d.add_argument("table")

    d.add_argument("--select", action="append", help="Filter: CODE=V1,V2 or CODE=* (omit filter)")

    d.add_argument("--format", default="json-stat2", choices=["json-stat", "json-stat2", "csv", "xlsx", "px"])

    d.add_argument("--output", help="Save the complete response to a file")
    d.add_argument("--codes", action="store_true", help="Display category codes instead of labels")
    d.add_argument("--pivot", default=None, help="Pivot dimension code (only for csv/xlsx per spec)")

    d.add_argument("--max-rows", type=int, default=200)

    d.add_argument("--pyjstat-hint", action="store_true")

    d.set_defaults(func=cmd_data)

    v = sub.add_parser("values", help="Find category codes by name, such as Lisdoonvarna")
    v.add_argument("subject")
    v.add_argument("product")
    v.add_argument("table")
    v.add_argument("--dimension")
    v.add_argument("--contains")
    v.set_defaults(func=cmd_values)
    return p

def main(argv: List[str]) -> int:

    parser = build_parser()

    args = parser.parse_args(argv)

    try:
        args.func(args)
    except OSError as exc:
        parser.exit(1, f"File error: {exc}\n")

    return 0

if __name__ == "__main__":

    raise SystemExit(main(sys.argv[1:]))

