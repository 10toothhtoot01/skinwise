"""Read rendered controls and capture responsive evidence before writing flow selectors.
Run against a running local server: SKINWISE_BASE_URL=http://127.0.0.1:3000 python tests/browser_inspect.py
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

base = os.environ.get('SKINWISE_BASE_URL', 'http://127.0.0.1:3000')
out = Path(os.environ.get('SKINWISE_EVIDENCE_DIR', 'test-results/browser'))
out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    evidence = []
    for name, width, height in [('desktop', 1440, 1000), ('mobile', 390, 844), ('narrow', 320, 740)]:
        page = browser.new_page(viewport={'width': width, 'height': height})
        errors = []
        page.on('pageerror', lambda err: errors.append(str(err)))
        page.goto(base)
        page.wait_for_load_state('networkidle')
        page.screenshot(path=str(out / f'{name}.png'), full_page=True)
        evidence.append({
            'viewport': name,
            'title': page.title(),
            'body': page.locator('body').inner_text(),
            'controls': page.locator('button, a, input, select, textarea').evaluate_all(
                '(els) => els.map(e => ({tag: e.tagName, text: e.innerText, type: e.type, label: e.getAttribute("aria-label"), id: e.id, disabled: e.disabled}))'),
            'horizontalOverflow': page.evaluate('document.documentElement.scrollWidth > window.innerWidth'),
            'uncaughtErrors': errors,
        })
        page.close()
    browser.close()
(out / 'inspection.json').write_text(json.dumps(evidence, indent=2))
print(json.dumps(evidence, indent=2))
