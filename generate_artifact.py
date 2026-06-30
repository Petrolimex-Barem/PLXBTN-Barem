import json
import os

json_file = "data/CHXD_219_BAREM_FINAL.json"
artifact_dir = r"C:\Users\PC01\.gemini\antigravity\brain\2f82948c-4c71-4e89-b700-eea123374fb7"
output_md = os.path.join(artifact_dir, "barem_219_be1.md")

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

be1_data = data.get("Barem bể 1", {})

# Sort heights
sorted_heights = sorted(be1_data.keys(), key=float)

# We want to format the 280 points in a clean multi-column table to make it readable.
# Let's make a table with 4 sets of (Height, Volume) columns:
# | H (cm) | V (Lít) | | H (cm) | V (Lít) | | H (cm) | V (Lít) | | H (cm) | V (Lít) |
num_cols = 4
rows_per_col = (len(sorted_heights) + num_cols - 1) // num_cols

table_rows = []
for i in range(rows_per_col):
    row_cells = []
    for c in range(num_cols):
        idx = i + c * rows_per_col
        if idx < len(sorted_heights):
            h = sorted_heights[idx]
            v = be1_data[h]
            # Format volume with comma thousands separator
            v_fmt = f"{v:,}" if isinstance(v, (int, float)) else str(v)
            row_cells.extend([f"**{h}**", v_fmt])
        else:
            row_cells.extend(["", ""])
    table_rows.append(row_cells)

with open(output_md, "w", encoding="utf-8") as f:
    f.write("# Bảng dữ liệu Barem Bể 1 - CHXD 219\n\n")
    f.write("Dưới đây là toàn bộ dữ liệu đã được hệ thống trích xuất từ sheet **Barem bể 1** của file **CHXD 219_BAREM_FINAL.xlsm**.\n")
    f.write("Hệ thống đã tự động chuyển đổi Chiều cao từ **mm sang cm** và giữ nguyên Thể tích đơn vị **Lít**.\n\n")
    
    # Write table header
    f.write("| H (cm) | V (Lít) | | H (cm) | V (Lít) | | H (cm) | V (Lít) | | H (cm) | V (Lít) |\n")
    f.write("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
    
    for row in table_rows:
        # Columns: h1, v1, h2, v2, h3, v3, h4, v4
        # Let's add empty columns as spacers
        f.write(f"| {row[0]} | {row[1]} | | {row[2]} | {row[3]} | | {row[4]} | {row[5]} | | {row[6]} | {row[7]} |\n")

print("Generated markdown table at:", output_md)
