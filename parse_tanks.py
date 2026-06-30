from bs4 import BeautifulSoup
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

html_path = "Bể chứa (Tank).html"
with open(html_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

tables = soup.find_all("table")
# Table 5 is the main one
table = tables[5]
rows = table.find_all("tr")

tank_mappings = {} # CHXD_ID -> {Tank_Num -> Product}

# Columns: 
# index 0: #
# index 1: Mã bể
# index 2: Mã TĐH
# index 3: Tên bể
# index 4: Tên tắt
# index 5: Hàng hóa
# index 6: CHXD
# index 7: Hiệu chỉnh barem ...

for row in rows[1:]:
    cells = [c.get_text().strip() for c in row.find_all(["td", "th"])]
    if len(cells) < 7:
        continue
        
    ten_be = cells[3]    # e.g., "Bể 01 - Dầu DO 0.05S-II"
    ten_tat = cells[4]   # e.g., "Bể 1"
    hang_hoa = cells[5]  # e.g., "Dầu Điêzen 0,05S Mức 2"
    chxd_text = cells[6] # e.g., "PETROLIMEX - CỬA HÀNG 101"
    
    # Extract store number
    chxd_match = re.search(r'CỬA HÀNG\s+([A-Za-z0-9_]+)', chxd_text, re.IGNORECASE)
    if not chxd_match:
        continue
    chxd_id = f"CHXD_{chxd_match.group(1).upper()}"
    
    # Extract tank number from 'Tên bể' or 'Tên tắt'
    # e.g., "Bể 01" -> "1", "Bể 05" -> "5"
    tank_match = re.search(r'Bể\s+0*(\d+)', ten_be, re.IGNORECASE)
    if not tank_match:
        # try 'ten_tat'
        tank_match = re.search(r'Bể\s+0*(\d+)', ten_tat, re.IGNORECASE)
        
    if not tank_match:
        continue
        
    tank_num = tank_match.group(1) # e.g., "1"
    
    # We want to format the product name cleanly.
    # We can extract the product from 'Tên bể' (the text after the hyphen)
    # e.g., "Bể 01 - Dầu DO 0.05S-II" -> "Dầu DO 0.05S-II"
    product = ten_be
    if " - " in ten_be:
        product = ten_be.split(" - ", 1)[1]
        
    if chxd_id not in tank_mappings:
        tank_mappings[chxd_id] = {}
        
    tank_mappings[chxd_id][tank_num] = {
        "full_name": ten_be,
        "product": product,
        "product_type": hang_hoa
    }

# Print sample mapping for CHXD_101
print("Sample parsed mapping for CHXD_101:")
if "CHXD_101" in tank_mappings:
    for t_num, t_info in sorted(tank_mappings["CHXD_101"].items()):
        print(f"  Bể {t_num} -> {t_info['product']} ({t_info['product_type']})")
        
# Check some general statistics
print(f"\nTotal stores parsed from HTML: {len(tank_mappings)}")
