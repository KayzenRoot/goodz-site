#!/usr/bin/env python3
"""Fail closed when security reports are missing, malformed or show known risk."""
from __future__ import annotations

import json
from pathlib import Path
import sys

REPORTS = Path(sys.argv[1] if len(sys.argv) > 1 else "reports")
UNKNOWN_LICENSES = {"", "UNKNOWN", "UNKNOWN LICENSE", "NOASSERTION"}


def load(name: str) -> dict | list | None:
    try:
        return json.loads((REPORTS / name).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"{name}: missing or invalid report: {exc}")
        return None


errors: list[str] = []
summary: list[str] = []

for report_name, label in (
    ("pip-audit-prod.json", "production"),
    ("pip-audit-dev.json", "development"),
):
    data = load(report_name)
    if data is None:
        continue
    dependencies = data.get("dependencies") if isinstance(data, dict) else None
    if not isinstance(dependencies, list) or not dependencies:
        errors.append(f"{report_name}: no audited dependencies")
        continue
    vulnerabilities = [
        f"{dep.get('name')}:{vuln.get('id')}"
        for dep in dependencies if isinstance(dep, dict)
        for vuln in (dep.get("vulns") or []) if isinstance(vuln, dict)
    ]
    if vulnerabilities:
        errors.append(f"{report_name}: known vulnerabilities: {', '.join(vulnerabilities)}")
    summary.append(f"SCA({label}) packages={len(dependencies)} vulnerabilities={len(vulnerabilities)}")

bandit = load("bandit.json")
if bandit is not None:
    results = bandit.get("results") if isinstance(bandit, dict) else None
    if not isinstance(results, list):
        errors.append("bandit.json: no results array")
    else:
        high = [
            f"{item.get('filename')}:{item.get('line_number')}:{item.get('test_id')}"
            for item in results
            if isinstance(item, dict) and item.get("issue_severity") == "HIGH"
        ]
        if high:
            errors.append(f"bandit.json: HIGH findings: {', '.join(high)}")
        summary.append(f"SAST findings={len(results)} high={len(high)}")

sbom = load("sbom.cdx.json")
if sbom is not None:
    components = sbom.get("components") if isinstance(sbom, dict) else None
    if not isinstance(sbom, dict) or sbom.get("bomFormat") != "CycloneDX":
        errors.append("sbom.cdx.json: not a CycloneDX document")
    elif not isinstance(components, list) or not components:
        errors.append("sbom.cdx.json: no components")
    else:
        summary.append(f"SBOM components={len(components)}")

licenses = load("licenses.json")
if licenses is not None:
    if not isinstance(licenses, list) or not licenses:
        errors.append("licenses.json: no packages")
    else:
        unknown = [
            item.get("Name", "<unnamed>")
            for item in licenses
            if not isinstance(item, dict)
            or str(item.get("License", "")).strip().upper() in UNKNOWN_LICENSES
        ]
        if unknown:
            errors.append(f"licenses.json: unknown licenses: {', '.join(unknown)}")
        summary.append(f"licenses packages={len(licenses)} unknown={len(unknown)}")

provenance = load("provenance.json")
if provenance is not None:
    if not isinstance(provenance, dict):
        errors.append("provenance.json: not an object")
    else:
        for key in ("commit", "workflow", "run_id", "run_attempt"):
            if not str(provenance.get(key, "")).strip():
                errors.append(f"provenance.json: missing {key}")
        if len(str(provenance.get("commit", ""))) != 40:
            errors.append("provenance.json: commit is not a full SHA")

print("; ".join(summary))
if errors:
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    raise SystemExit(1)
print("SECURITY_REPORTS_OK")
