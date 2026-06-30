import os
import re

# List of files we have
files = [f for f in os.listdir('data') if f.endswith('.json') and f.startswith('CHXD')]

# Mapping from image
# We'll parse the file number and try to find its mapping.
# Let's define the mapping from old number/id to new number/id.
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

unmapped = []
mapped_targets = {}

for f in files:
    # Extract number/id from filename
    # e.g., "CHXD_01_BAREM_UPDATE.json" -> "01"
    # "CHXD_2_BAREM_UPDATE.json" -> "2"
    # "CHXD_23A_BAREM_UPDATE.json" -> "23A"
    # "CHXD_219_BAREM_FINAL.json" -> "219"
    match = re.search(r'CHXD_([A-Za-z0-9]+)_', f)
    if match:
        old_id = match.group(1)
        if old_id == "219":
            continue
        # Check in mappings
        if old_id in mappings:
            mapped_targets[f] = f.replace(f"CHXD_{old_id}_", f"CHXD_{mappings[old_id]}_")
        else:
            # Try to see if key with leading zero or without leading zero matches
            alt_id = old_id.lstrip('0') if old_id.startswith('0') else '0' + old_id
            if alt_id in mappings:
                mapped_targets[f] = f.replace(f"CHXD_{old_id}_", f"CHXD_{mappings[alt_id]}_")
            else:
                unmapped.append((f, old_id))
    else:
        unmapped.append((f, None))

print("Unmapped files:")
for u in unmapped:
    print(u)

print("\nSample mapped files:")
for k, v in list(mapped_targets.items())[:5]:
    print(f"{k} -> {v}")
