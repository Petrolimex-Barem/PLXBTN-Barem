import os
import re
import json
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

def parse_barem_sheet(xl, sheet_name):
    df = xl.parse(sheet_name, header=None, engine="calamine")
    
    # We want to find H (cm) and V (lít)
    # Let's search row-by-row for cells containing 'h' and 'v'
    h_col_indices = []
    v_col_indices = []
    
    # Scan first 5 rows to find header positions
    header_row_idx = None
    for r_idx in range(min(10, len(df))):
        row_vals = [str(x).lower().strip() for x in df.iloc[r_idx]]
        
        # Find positions matching 'h (cm)' or just 'h'
        # And matching 'v (lít)' or 'v (l' or 'v'
        h_idxes = [c_idx for c_idx, val in enumerate(row_vals) if 'h' in val and ('cm' in val or val == 'h' or 'c.m' in val)]
        v_idxes = [c_idx for c_idx, val in enumerate(row_vals) if 'v' in val and ('lít' in val or 'lit' in val or val == 'v' or 'l.í' in val)]
        
        if len(h_idxes) > 0 and len(v_idxes) > 0:
            # Found header row
            header_row_idx = r_idx
            # Pair them up. Typically H is followed by V
            # e.g., if we have h_idxes like [0, 3, 6] and v_idxes like [1, 4, 7]
            h_col_indices = h_idxes
            v_col_indices = v_idxes
            break
            
    if header_row_idx is None:
        # Fallback: search for columns where cells have numbers and column titles contain H/V
        return None
        
    data = {}
    # Parse from header_row_idx + 1 onwards
    for r_idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[r_idx]
        for h_col, v_col in zip(h_col_indices, v_col_indices):
            if h_col < len(row) and v_col < len(row):
                h_val = row[h_col]
                v_val = row[v_col]
                
                # Check if h_val and v_val are numeric
                try:
                    # Convert to float/int
                    if pd.isna(h_val) or pd.isna(v_val):
                        continue
                    h_num = int(float(h_val))
                    v_num = int(float(v_val))
                    data[h_num] = v_num
                except (ValueError, TypeError):
                    continue
                    
    # Sort data by height
    sorted_data = {k: data[k] for k in sorted(data.keys())}
    return sorted_data

excel_file = "CHXD 01_BAREM_UPDATE 2023.xls"
xl = pd.ExcelFile(excel_file, engine="calamine")

station_data = {}
for sheet in xl.sheet_names:
    if "tra cuu" in sheet.lower():
        continue
    tank_data = parse_barem_sheet(xl, sheet)
    if tank_data:
        station_data[sheet] = tank_data
        
print("Parsed tank sheets:", list(station_data.keys()))
for tank, vals in station_data.items():
    print(f"{tank}: {len(vals)} points, min height: {min(vals.keys())}, max height: {max(vals.keys())}")
    # Print sample points
    sample_keys = list(vals.keys())[:5]
    print(f"  Sample: { {k: vals[k] for k in sample_keys} }")
