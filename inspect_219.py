import os
import pandas as pd

excel_file = "CHXD 219_BAREM_FINAL.xlsm"

with open("output_219.txt", "w", encoding="utf-8") as f:
    f.write(f"File exists: {os.path.exists(excel_file)}\n")
    try:
        xl = pd.ExcelFile(excel_file, engine="calamine")
        f.write(f"Sheets in file: {xl.sheet_names}\n")
        
        for sheet in xl.sheet_names:
            f.write(f"\n--- Sheet: {sheet} ---\n")
            try:
                df = xl.parse(sheet, nrows=10)
                f.write(df.head(5).to_string())
                f.write(f"\nColumns: {df.columns.tolist()}\n")
            except Exception as e:
                f.write(f"Error reading sheet {sheet}: {e}\n")
    except Exception as e:
        f.write(f"Error opening Excel file: {e}\n")
