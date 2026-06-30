from bs4 import BeautifulSoup
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

html_path = "Bể chứa (Tank).html"
with open(html_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

tables = soup.find_all("table")
print(f"Number of tables: {len(tables)}")

for idx in range(2, len(tables)):
    table = tables[idx]
    print(f"\n--- Table {idx} ---")
    rows = table.find_all("tr")
    print(f"Rows count: {len(rows)}")
    for r_idx, row in enumerate(rows[:10]):
        cells = [c.get_text().strip().replace('\n', ' ') for c in row.find_all(["td", "th"])]
        print(f"Row {r_idx}: {cells[:15]}")
