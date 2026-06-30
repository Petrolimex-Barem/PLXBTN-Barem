import os
import json

data_dir = "data"
files = [f for f in os.listdir(data_dir) if f.endswith('.json') and f.startswith('CHXD')]

decimal_stations = []

for f in files:
    path = os.path.join(data_dir, f)
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
        has_decimals = False
        decimal_count = 0
        total_count = 0
        
        for tank, points in data.items():
            for h, v in points.items():
                total_count += 1
                # Check if volume is float and has a fractional part
                if isinstance(v, float) and not v.is_integer():
                    has_decimals = True
                    decimal_count += 1
                    
        if has_decimals:
            decimal_stations.append({
                "filename": f,
                "decimal_points": decimal_count,
                "total_points": total_count,
                "percentage": round((decimal_count / total_count) * 100, 1)
            })
    except Exception as e:
        print(f"Error reading {f}: {e}")

print(f"Total stations with decimal volumes: {len(decimal_stations)} / {len(files)}")
print("\nList of stations with decimal volumes:")
for s in sorted(decimal_stations, key=lambda x: x['filename']):
    print(f"  {s['filename']}: {s['decimal_points']} decimal points out of {s['total_points']} ({s['percentage']}%)")
