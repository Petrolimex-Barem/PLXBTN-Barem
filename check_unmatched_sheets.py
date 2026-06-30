import json
import re

with open("data/stations.json", "r", encoding="utf-8") as f:
    stations = json.load(f)
    
s_106 = next((s for s in stations if "106" in s["id"]), None)
s_116 = next((s for s in stations if "116" in s["id"]), None)

with open("unmatched_sheets_info.txt", "w", encoding="utf-8") as out:
    out.write("CHXD 106 entry in stations.json:\n")
    out.write(str(s_106) + "\n")
    out.write("\nCHXD 116 entry in stations.json:\n")
    out.write(str(s_116) + "\n")

    # Read HTML file for 106 and 116
    from bs4 import BeautifulSoup
    html_path = "Bể chứa (Tank).html"
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    table = soup.find_all("table")[5]
    rows = table.find_all("tr")

    out.write("\nHTML entries for 106:\n")
    for row in rows[1:]:
        cells = [c.get_text().strip() for c in row.find_all(["td", "th"])]
        if len(cells) < 7:
            continue
        chxd_text = cells[6]
        if "106" in chxd_text:
            out.write(" | ".join([cells[3], cells[4], cells[5], cells[10], cells[11]]) + "\n")
            
    out.write("\nHTML entries for 116:\n")
    for row in rows[1:]:
        cells = [c.get_text().strip() for c in row.find_all(["td", "th"])]
        if len(cells) < 7:
            continue
        chxd_text = cells[6]
        if "116" in chxd_text:
            out.write(" | ".join([cells[3], cells[4], cells[5], cells[10], cells[11]]) + "\n")

print("Wrote output to unmatched_sheets_info.txt")
