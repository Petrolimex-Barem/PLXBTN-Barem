import os
import re
import json

data_dir = "data"

# Map old number codes to new number codes
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

# 1. Delete CHXD 5 and 129
files_to_delete = ["CHXD_5_BAREM_UPDATE.json", "CHXD_129_BAREM_UPDATE.json"]
for f_del in files_to_delete:
    path = os.path.join(data_dir, f_del)
    if os.path.exists(path):
        os.remove(path)
        print(f"Deleted: {path}")

# 2. Rename remaining files
files = [f for f in os.listdir(data_dir) if f.endswith('.json') and f.startswith('CHXD')]
renamed_map = {} # old_id -> new_id for updating stations.json

for f in files:
    if f == "CHXD_219_BAREM_FINAL.json":
        continue
        
    match = re.search(r'CHXD_([A-Za-z0-9]+)_', f)
    if match:
        old_id = match.group(1)
        new_id = mappings.get(old_id)
        if not new_id:
            # Check with/without leading zero
            alt_id = old_id.lstrip('0') if old_id.startswith('0') else '0' + old_id
            new_id = mappings.get(alt_id)
            
        if new_id:
            new_filename = f.replace(f"CHXD_{old_id}_", f"CHXD_{new_id}_")
            old_path = os.path.join(data_dir, f)
            new_path = os.path.join(data_dir, new_filename)
            
            # Avoid naming conflicts if destination exists (should not happen if we rename one by one carefully)
            if os.path.exists(new_path):
                os.remove(new_path)
            os.rename(old_path, new_path)
            
            # Record mapping for stations.json update
            old_full_id = f.replace('.json', '')
            new_full_id = new_filename.replace('.json', '')
            renamed_map[old_full_id] = (new_full_id, old_id, new_id)
            print(f"Renamed: {f} -> {new_filename}")
        else:
            print(f"Warning: No mapping found for {f}")

# 3. Update stations.json
stations_path = os.path.join(data_dir, "stations.json")
if os.path.exists(stations_path):
    with open(stations_path, "r", encoding="utf-8") as f:
        stations = json.load(f)
        
    updated_stations = []
    for s in stations:
        # Check if this station is deleted (CHXD 5 or 129)
        if s["id"] in ["CHXD_5_BAREM_UPDATE", "CHXD_129_BAREM_UPDATE"]:
            print(f"Removing index entry for deleted station: {s['id']}")
            continue
            
        if s["id"] in renamed_map:
            new_full_id, old_id, new_id = renamed_map[s["id"]]
            
            # Update s
            s["id"] = new_full_id
            # Replace old_id with new_id in the name
            # e.g., "CHXD 01 BAREM UPDATE 2023" -> "CHXD 101 BAREM UPDATE 2023"
            # we look for "CHXD " + old_id and replace with "CHXD " + new_id
            # to be safe, replace word old_id with new_id
            s["name"] = s["name"].replace(f"CHXD {old_id}", f"CHXD {new_id}").replace(f"CHXD {int(old_id) if old_id.isdigit() else old_id}", f"CHXD {new_id}")
            s["filename"] = s["filename"].replace(f"CHXD {old_id}", f"CHXD {new_id}").replace(f"CHXD {int(old_id) if old_id.isdigit() else old_id}", f"CHXD {new_id}")
            updated_stations.append(s)
        elif s["id"] == "CHXD_219_BAREM_FINAL":
            # Keep 219
            updated_stations.append(s)
        else:
            print(f"Warning: Station {s['id']} not updated in stations.json")
            updated_stations.append(s)
            
    # Sort updated stations naturally by new ID number
    def get_station_num(s):
        match = re.search(r'CHXD_([A-Za-z0-9]+)_', s["id"])
        if match:
            val = match.group(1)
            # return digits if it is digit
            digits = re.findall(r'\d+', val)
            if digits:
                return int(digits[0])
        return 9999
        
    updated_stations.sort(key=get_station_num)
            
    with open(stations_path, "w", encoding="utf-8") as f:
        json.dump(updated_stations, f, ensure_ascii=False, indent=2)
        print("Updated stations.json successfully.")
