"""Dependency-free XLSX/PDF export and reopen checks for synthetic QA reports."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

DISCLAIMER = "ข้อมูลจำลองสำหรับทดสอบระบบ ไม่ใช่คำแนะนำลงทุน"


def canonical_json(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _xlsx_sheet(rows: list[list[object]]) -> str:
    rendered = []
    for r, row in enumerate(rows, 1):
        cells = []
        for c, value in enumerate(row, 1):
            col = ""
            n = c
            while n:
                n, rem = divmod(n - 1, 26); col = chr(65 + rem) + col
            cells.append(f'<c r="{col}{r}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>')
        rendered.append(f'<row r="{r}">{"".join(cells)}</row>')
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">' \
        f'<sheetData>{"".join(rendered)}</sheetData></worksheet>'


def export_xlsx(report: dict, path: str | Path) -> None:
    summary = [["SYNTHETIC_DEMO"], [DISCLAIMER], ["Run Summary"],
               ["run_id", report.get("run_id")], ["scope", report.get("scope")]]
    for gate, result in report["gates"].items():
        summary.append([gate, result["status"], ", ".join(result.get("blockers", []))])
    companies = [["ticker", "company", "status", "reason", "transition", "data QA", "thesis/valuation QA", "blockers", "5Y history", "5Y reason", "actionable buy"]]
    for stock in report["stocks"]:
        history = stock["history_5y"]
        companies.append([stock["ticker"], stock["company"], stock["status"], stock["status_reason"],
                          stock["transition_condition"], stock["gates"]["data_qa"],
                          stock["gates"]["thesis_valuation_qa"], ", ".join(stock["blockers"]),
                          history.get("value", "N/A"), history.get("reason", ""), stock["actionable_buy"]])
    qa = [["SYNTHETIC_DEMO"], [DISCLAIMER], ["validated_dataset_sha256", hashlib.sha256(canonical_json(report).encode()).hexdigest()],
          ["production_ready", report["production_ready"]], ["stub_blockers", ", ".join(report["stub_blockers"])]]
    sheets = [("Run Summary", summary), ("บริษัทตัวอย่าง", companies), ("QA", qa)]
    content_types = '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>' + ''.join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1,4)) + '</Types>'
    workbook = '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' + ''.join(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>' for i,(name,_) in enumerate(sheets,1)) + '</sheets></workbook>'
    root_rels = '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    wb_rels = '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1,4)) + '</Relationships>'
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types); archive.writestr("_rels/.rels", root_rels)
        archive.writestr("xl/workbook.xml", workbook); archive.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        for i, (_, rows) in enumerate(sheets, 1): archive.writestr(f"xl/worksheets/sheet{i}.xml", _xlsx_sheet(rows))


def inspect_xlsx(path: str | Path, report: dict) -> dict:
    try:
        with zipfile.ZipFile(path) as archive:
            texts = []
            for name in ("xl/worksheets/sheet1.xml", "xl/worksheets/sheet2.xml", "xl/worksheets/sheet3.xml"):
                root = ET.fromstring(archive.read(name)); texts.extend(node.text or "" for node in root.iter() if node.tag.endswith("}t"))
        required = ["SYNTHETIC_DEMO", DISCLAIMER, *[s["ticker"] for s in report["stocks"]]]
        return {"code": "xlsx_reopen_matches_dataset", "result": "PASS" if all(x in texts for x in required) else "FAIL"}
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError):
        return {"code": "xlsx_reopen_matches_dataset", "result": "FAIL"}


def export_pdf(report: dict, path: str | Path) -> None:
    # A compact, standards-readable synthetic PDF. Thai source text is preserved
    # in UTF-8 metadata; visual Thai rendering needs a licensed Thai font/runtime.
    lines = ["SYNTHETIC_DEMO", "SYNTHETIC SYSTEM TEST - NOT INVESTMENT ADVICE", "Run Summary", str(report.get("scope"))]
    lines += [f'{s["ticker"]} | {s["status"]} | blockers: {", ".join(s["blockers"]) or "none"}' for s in report["stocks"]]
    stream = "BT /F1 10 Tf 40 800 Td 14 TL " + " ".join(f"({line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')}) Tj T*" for line in lines) + " ET"
    metadata = canonical_json(report).encode("utf-8").hex()
    objects = [b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj", b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj",
               b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 595 842]/Resources<</Font<</F1 5 0 R>>>>/Contents 4 0 R>>endobj",
               f"4 0 obj<</Length {len(stream.encode())}>>stream\n{stream}\nendstream endobj".encode(),
               b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj"]
    out = bytearray(b"%PDF-1.4\n"); offsets = [0]
    for obj in objects: offsets.append(len(out)); out.extend(obj + b"\n")
    xref = len(out); out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]: out.extend(f"{offset:010d} 00000 n \n".encode())
    out.extend(f"trailer<</Size {len(objects)+1}/Root 1 0 R>>\nstartxref\n{xref}\n%%EOF\n%THAI_UTF8_HEX:{metadata}\n".encode())
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(out)


def inspect_pdf(path: str | Path, report: dict) -> list[dict]:
    data = Path(path).read_bytes()
    marker = b"%THAI_UTF8_HEX:"
    payload = data.split(marker, 1)[1].strip() if marker in data else b""
    expected = canonical_json(report)
    return [
        {"code": "pdf_reopen_matches_dataset", "result": "PASS" if data.startswith(b"%PDF-") and payload and bytes.fromhex(payload.decode()).decode() == expected else "FAIL"},
        {"code": "pdf_visual_thai_render", "result": "STUB", "reason": "thai_font_and_pdf_renderer_unavailable"},
    ]
