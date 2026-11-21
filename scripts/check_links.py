#!/usr/bin/env python3
"""Check every competitor link in .hackathon/ideas/sdg-*.md and .hackathon/chosen-idea.md.

Usage: python check_links.py <project-root> [--format md|json]
Classes: ok (2xx/3xx) · dead (404/410, DNS/connection failure) · blocked (401/403/405/429/5xx/timeout:
the site refuses bots, so it can't be auto-verified). Exit 1 if any link is dead.
"""
import concurrent.futures as cf
import glob
import json
import os
import re
import socket
import ssl
import sys
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (compatible; hackathon-link-check/1.0)"
URL_RE = re.compile(r"https?://[^\s|)<>\]]+")
ID_RE = re.compile(r"^## \[(SDG\d+-\d+)\]", re.M)


def collect(root):
    hk = os.path.join(root, ".hackathon")
    files = sorted(glob.glob(os.path.join(hk, "ideas", "sdg-*.md")))
    chosen = os.path.join(hk, "chosen-idea.md")
    if os.path.exists(chosen):
        files.append(chosen)
    links = []
    for fp in files:
        current = os.path.basename(fp)
        for line in open(fp, encoding="utf-8").read().splitlines():
            m = ID_RE.match(line)
            if m:
                current = m.group(1)
            if line.strip().startswith("|"):
                for url in URL_RE.findall(line):
                    links.append({"idea": current, "file": os.path.basename(fp), "url": url.rstrip(".,")})
    return links


def check(url):
    status, detail = _check(url, None)
    if status != "ok" and "CERTIFICATE_VERIFY_FAILED" in str(detail):
        # Local Python often lacks a CA bundle (common on Windows). We only test that the page
        # exists and send no data, so retry without certificate verification.
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        status, detail = _check(url, ctx)
        detail = f"{detail} (TLS not verified locally)"
    return status, detail


def _check(url, ctx):
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
                return "ok", r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 400, 501):
                continue  # some servers reject HEAD; retry with GET
            if e.code in (404, 410):
                return "dead", e.code
            return "blocked", e.code
        except urllib.error.URLError as e:
            reason = e.reason
            if isinstance(reason, socket.gaierror):
                return "dead", "DNS failure"
            if isinstance(reason, (socket.timeout, TimeoutError)):
                return "blocked", "timeout"
            if method == "HEAD":
                continue
            if isinstance(reason, ConnectionRefusedError):
                return "dead", "connection refused"
            return "blocked", str(reason)[:80]
        except (socket.timeout, TimeoutError):
            return "blocked", "timeout"
        except Exception as e:  # noqa: BLE001
            if method == "HEAD":
                continue
            return "blocked", type(e).__name__
    return "blocked", "unknown"


def main(argv):
    args = argv[1:]
    fmt = "md"
    if "--format" in args:
        i = args.index("--format"); fmt = args[i + 1]; del args[i:i + 2]
    if len(args) != 1:
        print(__doc__); return 2
    links = collect(args[0])
    uniq = sorted({l["url"] for l in links})
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        results = dict(zip(uniq, ex.map(check, uniq)))
    for l in links:
        l["status"], l["detail"] = results[l["url"]]
    if fmt == "json":
        print(json.dumps(links, indent=2))
    else:
        counts = {s: sum(1 for l in links if l["status"] == s) for s in ("ok", "dead", "blocked")}
        print(f"{len(links)} links ({len(uniq)} unique): ok {counts['ok']} · dead {counts['dead']} · blocked {counts['blocked']}")
        for l in links:
            if l["status"] != "ok":
                print(f"- {l['status'].upper():7} {l['idea']:10} {l['url']} ({l['detail']})")
    return 1 if any(l["status"] == "dead" for l in links) else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main(sys.argv))
