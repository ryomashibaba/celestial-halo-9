#!/usr/bin/env python3
"""Rebuild the local offline plotly.min.js from the installed Plotly Python distribution."""
from pathlib import Path
from plotly.offline import get_plotlyjs
p=Path(__file__).resolve().parent/'plotly.min.js'
p.write_text(get_plotlyjs(),encoding='utf-8')
print(f'Offline plotly.js: {p.stat().st_size:,} bytes -> {p}')
