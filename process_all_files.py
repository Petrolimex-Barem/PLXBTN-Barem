import os
import re
import json
import sys
import io
import msoffcrypto
import pandas as pd
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

# 1. Parse Tank Mappings from HTML
html_path = "Bể chứa (Tank).html"
tank_mappings = {}
if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    table = soup.find_all("table")[5]
    rows = table.find_all("tr")
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

# 2. Store Mappings (Old -> New)
mappings = {
    "01": "101", "2": "102", "4": "104", "06": "106", "07": "107", "08": "108", "09": "109",
    "10": "110", "11": "111", "12": "112", "13": "113", "14": "114", "15": "115", "16": "116",
    "17": "117", "18": "118", "19": "119", "20": "120", "21": "121", "22": "122",
    "23A": "105", "23B": "123", "25": "125", "27": "127", "28": "128", "29": "129", "30": "130",
    "31": "131", "33": "133", "36": "136", "37": "137", "39A": "124", "39B": "126",
    "40": "140", "41": "141", "42": "142", "43": "143", "44": "144", "45": "145", "46": "146",
    "47": "147", "48": "148", "49": "149", "50": "150", "51": "151", "52": "152", "53": "153",
    "54": "154", "55": "155", "56": "156", "57": "157", "59": "159",
    "61A": "132", "61B": "134", "62": "162", "63": "163", "64": "164", "68": "168", "69": "169",
    "70": "170", "72": "172", "73": "173", "74": "174", "75": "175", "76": "176", "77": "177",
    "78": "178", "79": "179", "81": "181", "82": "182", "83": "183", "84": "184", "85": "185",
    "86": "186", "87": "187", "88": "188", "89": "189", "90": "190", "91": "191", "92": "192",
    "93": "193", "94": "194", "95": "195", "96": "196", "97": "197", "98": "198", "99": "199",
    "100": "200", "101": "201", "102": "202", "103": "203", "104": "204", "105": "205",
    "106": "206", "107": "207", "108": "208", "109": "209", "110": "210", "111": "211",
    "112": "212", "113": "213", "114": "214", "115": "215", "116": "216", "117": "135",
    "122": "138", "123": "139", "124": "158", "125": "160", "126": "161", "127": "165",
    "130": "166", "131": "167", "132": "171", "133": "180"
}

def parse_barem_sheet(xl, sheet_name):
    try:
        df = xl.parse(sheet_name, header=None, engine="calamine")
    except Exception as e:
        print(f"Error parsing sheet {sheet_name}: {e}")
        return None
        
    h_col_indices = []
    v_col_indices = []
    
    header_row_idx = None
    for r_idx in range(min(50, len(df))):
        row_vals = [str(x).lower().strip() for x in df.iloc[r_idx]]
        h_idxes = []
        v_idxes = []
        for c_idx, val in enumerate(row_vals):
            val_clean = val.replace(" ", "")
            if 'height' in val_clean or 'h(cm)' in val_clean or 'h(mm)' in val_clean or '(h)' in val_clean or val_clean == 'h' or 'c.m' in val_clean:
                h_idxes.append(c_idx)
            elif ('volume' in val_clean or 'v(lít)' in val_clean or 'v(lit)' in val_clean or 'v(l)' in val_clean or '(v)' in val_clean or val_clean == 'v' or 'l.í' in val_clean or 'lít' in val_clean or 'lit' in val_clean) and '/' not in val_clean:
                v_idxes.append(c_idx)
                
        if len(h_idxes) > 0 and len(v_idxes) > 0:
            header_row_idx = r_idx
            h_col_indices = h_idxes
            v_col_indices = v_idxes
            break
            
    if header_row_idx is None:
        return None
        
    raw_points = []
    for r_idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[r_idx]
        for h_col, v_col in zip(h_col_indices, v_col_indices):
            if h_col < len(row) and v_col < len(row):
                h_val = row[h_col]
                v_val = row[v_col]
                try:
                    if pd.isna(h_val) or pd.isna(v_val):
                        continue
                    h_num = float(h_val)
                    v_num = float(v_val)
                    raw_points.append((h_num, v_num))
                except (ValueError, TypeError):
                    continue
                    
    if not raw_points:
        return None
        
    # Check if heights are in mm (max height > 500)
    max_h = max(p[0] for p in raw_points)
    use_mm_conversion = max_h > 500
    
    data = {}
    for h_num, v_num in raw_points:
        if use_mm_conversion:
            h_num = h_num / 10.0
            
        if v_num == 0 and h_num > 10:
            continue
            
        if h_num.is_integer():
            h_num = int(h_num)
        else:
            h_num = round(h_num, 1)
            
        if v_num.is_integer():
            v_num = int(v_num)
        else:
            v_num = round(v_num, 1)
            
        data[h_num] = v_num
        
    return {str(k): data[k] for k in sorted(data.keys())}

def clean_station_id(filename):
    match = re.search(r'CHXD\s+(\d+[A-Z]?)', filename, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return filename.split('.')[0]

def main():
    # Clean and recreate data directory to prevent conflicts
    import shutil
    if os.path.exists("data"):
        shutil.rmtree("data")
    os.makedirs("data", exist_ok=True)
    
    files = [f for f in os.listdir('.') if f.endswith(('.xls', '.xlsx', '.xlsm')) and f.startswith("CHXD")]
    files.sort(key=lambda x: [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', x)])
    
    stations_dict = {}
    
    def get_file_year(fname):
        match = re.search(r'(202\d)', fname)
        return int(match.group(1)) if match else 0
    
    for idx, filename in enumerate(files):
        old_num = clean_station_id(filename)
        new_num = old_num
        
        # Generate new file ID and station name
        new_station_id = f"CHXD_{new_num}_BAREM"
        new_filename = filename
            
        new_station_name = new_filename.split('.')[0].replace('_', ' ')
        new_station_name = re.sub(r'\s+', ' ', new_station_name).strip()
        
        print(f"Processing ({idx+1}/{len(files)}): {filename} -> {new_station_id} ({new_station_name})")
        
        try:
            # Try normal load first
            try:
                xl = pd.ExcelFile(filename, engine="calamine")
            except Exception:
                # Decrypt using VelvetSweatshop if encrypted
                decrypted = io.BytesIO()
                with open(filename, "rb") as f:
                    office_file = msoffcrypto.OfficeFile(f)
                    office_file.load_key(password="VelvetSweatshop")
                    office_file.decrypt(decrypted)
                decrypted.seek(0)
                xl = pd.ExcelFile(decrypted, engine="calamine")
                
            station_data = {}
            for sheet in xl.sheet_names:
                if "tra cuu" in sheet.lower():
                    continue
                tank_data = parse_barem_sheet(xl, sheet)
                if tank_data:
                    if new_num == "145" and ("bể 2" in sheet.lower() or "be 2" in sheet.lower()):
                        tank_data = {k: v for k, v in tank_data.items() if float(k) <= 172}
                    station_data[sheet] = tank_data
            
            if station_data:
                final_station_data = station_data
                tanks_info = {}
                for tank_sheet in station_data.keys():
                    sheet_num_match = re.search(r'b[eể]\s+0*(\d+)', tank_sheet, re.IGNORECASE)
                    if sheet_num_match:
                        sheet_num = sheet_num_match.group(1)
                        if new_num in tank_mappings and sheet_num in tank_mappings[new_num]:
                            tanks_info[tank_sheet] = f"Bể {sheet_num} - {tank_mappings[new_num][sheet_num]}"
                
                # Check if we already processed a newer version of this station
                current_year = get_file_year(filename)
                existing_station = stations_dict.get(new_station_id)
                if existing_station:
                    existing_year = get_file_year(existing_station["filename"])
                    if current_year < existing_year:
                        print(f"  Skipping older duplicate file: {filename} (year: {current_year} < existing: {existing_year})")
                        continue
                
                # Write individual json data
                with open(f"data/{new_station_id}.json", "w", encoding="utf-8") as f_out:
                    json.dump(final_station_data, f_out, ensure_ascii=False, indent=2)
                
                stations_dict[new_station_id] = {
                    "id": new_station_id,
                    "name": new_station_name,
                    "filename": new_filename,
                    "tanks": list(final_station_data.keys()),
                    "tanks_info": tanks_info
                }
                print(f"  Success: Parsed {len(final_station_data)} tanks (year: {current_year})")
            else:
                print(f"  Warning: No barem data found in {filename}")
        except Exception as e:
            print(f"  Error processing {filename}: {e}")
            
    # Sort updated stations naturally by new ID number
    stations_list = list(stations_dict.values())
    
    def get_station_num(s):
        match = re.search(r'CHXD_([A-Za-z0-9]+)_', s["id"])
        if not match:
            match = re.search(r'CHXD_([A-Za-z0-9]+)', s["id"])
        if match:
            val = match.group(1)
            digits = re.findall(r'\d+', val)
            if digits:
                return int(digits[0])
        return 9999
        
    stations_list.sort(key=get_station_num)
    
    # Save the index file
    with open("data/stations.json", "w", encoding="utf-8") as f:
        json.dump(stations_list, f, ensure_ascii=False, indent=2)
        
    print(f"Done! Successfully processed {len(stations_list)} stations.")

if __name__ == "__main__":
    main()
