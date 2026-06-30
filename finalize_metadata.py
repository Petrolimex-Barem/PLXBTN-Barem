import json
import re
from bs4 import BeautifulSoup

html_path = "Bể chứa (Tank).html"
with open(html_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

table = soup.find_all("table")[5]
rows = table.find_all("tr")

tank_mappings = {}
for row in rows[1:]:
    cells = [c.get_text().strip() for c in row.find_all(["td", "th"])]
    if len(cells) < 7:
        continue
    ten_be = cells[3]
    ten_tat = cells[4]
    hang_hoa = cells[5]
    chxd_text = cells[6]
    
    chxd_match = re.search(r'CỬA HÀNG\s+([A-Za-z0-9_]+)', chxd_text, re.IGNORECASE)
    if not chxd_match:
        continue
    chxd_id = chxd_match.group(1).upper()
    
    tank_match = re.search(r'Bể\s+0*(\d+)', ten_be, re.IGNORECASE)
    if not tank_match:
        tank_match = re.search(r'Bể\s+0*(\d+)', ten_tat, re.IGNORECASE)
        
    if not tank_match:
        continue
        
    tank_num = tank_match.group(1)
    
    product = ten_be
    if " - " in ten_be:
        product = ten_be.split(" - ", 1)[1]
        
    if chxd_id not in tank_mappings:
        tank_mappings[chxd_id] = {}
    tank_mappings[chxd_id][tank_num] = product

# Load stations.json
stations_path = "data/stations.json"
with open(stations_path, "r", encoding="utf-8") as f:
    stations = json.load(f)

for s in stations:
    num_match = re.search(r'CHXD_([A-Za-z0-9]+)_', s["id"])
    if not num_match:
        num_match = re.search(r'CHXD_([A-Za-z0-9]+)', s["id"])
        
    if num_match:
        store_num = num_match.group(1).upper()
        s["tanks_info"] = {}
        
        # Hardcode manual fallback for 106 and 116
        if store_num == "106":
            s["tanks_info"] = {
                "Barem 10m3 (95-95V-Do)": "Bể 3 - Xăng E10 RON 95 Mức 5",
                "Barem 20m3 (Do 0,05)": "Bể 1 - Dầu DO 0.05S-II"
            }
            continue
        elif store_num == "116":
            s["tanks_info"] = {
                "Barem 10m3 (95)": "Bể 1 - Xăng E10 RON 95 Mức 5",
                "Barem 25m3 (Do 0,05)": "Bể 3 - Dầu DO 0.05S-II"
            }
            continue
            
        if store_num in tank_mappings:
            for tank_sheet in s["tanks"]:
                sheet_num_match = re.search(r'bể\s+0*(\d+)', tank_sheet, re.IGNORECASE)
                if sheet_num_match:
                    sheet_num = sheet_num_match.group(1)
                    if sheet_num in tank_mappings[store_num]:
                        s["tanks_info"][tank_sheet] = f"Bể {sheet_num} - {tank_mappings[store_num][sheet_num]}"

# Write the updated stations.json
with open(stations_path, "w", encoding="utf-8") as f:
    json.dump(stations, f, ensure_ascii=False, indent=2)
print("stations.json has been fully updated and saved!")
