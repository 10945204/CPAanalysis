#!/usr/bin/env python3
"""Generate a polished SVG summary visual for CPA alternative pathways survey data."""

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "Alternative CPA Pathways Survey_December 31, 2025_09.45.csv"
OUTPUT_PATH = ROOT / "visuals" / "cpa_survey_key_findings.svg"

QUESTIONS = [
    ("Q29", "Likelihood of pursuing CPA license"),
    ("Q51", "Alternative pathway's impact on CPA desire"),
    ("Q52", "Alternative pathway's impact on graduate degree desire"),
    ("Q6", "Overall perception of CPA pathway change"),
    ("Q25", "Attractiveness of shorter graduate certificate"),
]

ORDER = {
    "Very unlikely": 0,
    "Somewhat unlikely": 1,
    "Neither likely nor unlikely": 2,
    "Somewhat likely": 3,
    "Very likely": 4,
    "Significantly decreased desire": 0,
    "Decreased desire": 1,
    "No change in desire": 2,
    "Increased desire": 3,
    "Significantly increased desire": 4,
    "Very Negative": 0,
    "Somewhat Negative": 1,
    "Neutral": 2,
    "Somewhat Positive": 3,
    "Very Positive": 4,
    "Not at all attractive": 0,
    "Somewhat unattractive": 1,
    "Neither attractive nor unattractive": 2,
    "Somewhat attractive": 3,
    "Very attractive": 4,
}

COLOR_SCALE = {
    0: "#8b1e3f",  # deep negative
    1: "#d8576b",  # negative
    2: "#b0b7c3",  # neutral
    3: "#58a4b0",  # positive
    4: "#1d7a8c",  # deep positive
}


def load_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    clean = [
        r
        for r in rows
        if r.get("ResponseId")
        and r.get("StartDate") != "Start Date"
        and r.get("Finished") == "True"
    ]
    return clean


def summarize(rows, column):
    counter = Counter(r[column].strip() for r in rows if r[column].strip())
    ordered = sorted(counter.items(), key=lambda kv: ORDER.get(kv[0], 999))
    total = sum(counter.values())
    return ordered, total


def make_svg(results, n_finished):
    width = 1400
    height = 980
    left_margin = 90
    chart_left = 520
    chart_width = 780
    top_margin = 170
    row_gap = 140
    bar_height = 46

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs>',
        '  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">',
        '    <stop offset="0%" stop-color="#f7f9fc"/>',
        '    <stop offset="100%" stop-color="#edf1f8"/>',
        '  </linearGradient>',
        '  <filter id="cardShadow" x="-10%" y="-10%" width="130%" height="130%">',
        '    <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#8fa2c0" flood-opacity="0.2"/>',
        '  </filter>',
        '</defs>',
        '<rect x="0" y="0" width="1400" height="980" fill="url(#bg)"/>',
        '<text x="90" y="72" font-size="44" font-family="Segoe UI, Arial, sans-serif" font-weight="700" fill="#1d2d44">CPA Pathway Survey: Key Findings</text>',
        '<text x="90" y="110" font-size="22" font-family="Segoe UI, Arial, sans-serif" fill="#334e68">Distribution of responses across five high-impact decision questions</text>',
        f'<text x="90" y="140" font-size="18" font-family="Segoe UI, Arial, sans-serif" fill="#486581">n = {n_finished} completed responses</text>',
    ]

    for i, (label, entries, total) in enumerate(results):
        y = top_margin + i * row_gap
        parts.append(f'<rect x="70" y="{y - 44}" width="1260" height="92" rx="16" fill="#ffffff" filter="url(#cardShadow)"/>')
        parts.append(f'<text x="{left_margin}" y="{y - 8}" font-size="22" font-family="Segoe UI, Arial, sans-serif" font-weight="600" fill="#102a43">{label}</text>')

        x = chart_left
        for text, count in entries:
            pct = (count / total) * 100 if total else 0
            seg_w = max(1.0, chart_width * (count / total)) if total else 0
            tone = ORDER.get(text, 2)
            color = COLOR_SCALE.get(tone, "#6b778d")
            parts.append(
                f'<rect x="{x:.1f}" y="{y}" width="{seg_w:.1f}" height="{bar_height}" fill="{color}"/>'
            )

            if seg_w > 115:
                parts.append(
                    f'<text x="{x + seg_w/2:.1f}" y="{y + 21}" text-anchor="middle" font-size="13" font-family="Segoe UI, Arial, sans-serif" fill="#ffffff" font-weight="600">{text}</text>'
                )
                parts.append(
                    f'<text x="{x + seg_w/2:.1f}" y="{y + 39}" text-anchor="middle" font-size="15" font-family="Segoe UI, Arial, sans-serif" fill="#ffffff" font-weight="700">{pct:.1f}%</text>'
                )
            else:
                parts.append(
                    f'<text x="{x + seg_w + 6:.1f}" y="{y + 28}" font-size="13" font-family="Segoe UI, Arial, sans-serif" fill="#334e68">{pct:.1f}%</text>'
                )
            x += seg_w

    parts.extend(
        [
            '<text x="90" y="940" font-size="14" font-family="Segoe UI, Arial, sans-serif" fill="#627d98">Source: Alternative CPA Pathways Survey (cleaned to completed responses only).</text>',
            '</svg>',
        ]
    )
    return "\n".join(parts)


def main():
    rows = load_rows(CSV_PATH)
    results = []
    for col, label in QUESTIONS:
        entries, total = summarize(rows, col)
        results.append((label, entries, total))

    svg = make_svg(results, len(rows))
    OUTPUT_PATH.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
