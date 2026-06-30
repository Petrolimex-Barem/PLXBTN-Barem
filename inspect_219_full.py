import pandas as pd

excel_file = "CHXD 219_BAREM_FINAL.xlsm"
xl = pd.ExcelFile(excel_file, engine="calamine")
df = xl.parse("Barem bể 1", header=None)

with open("output_219_full.txt", "w", encoding="utf-8") as f:
    for idx, row in df.iterrows():
        f.write(f"Row {idx}: {row.tolist()}\n")
