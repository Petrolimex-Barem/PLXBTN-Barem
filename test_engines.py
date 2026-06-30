import pandas as pd

file = "CHXD 31_BAREM_UPDATE 2023.xls"
print("Trying calamine...")
try:
    xl = pd.ExcelFile(file, engine="calamine")
    print("Success with calamine. Sheets:", xl.sheet_names)
except Exception as e:
    print("Failed with calamine:", e)

print("\nTrying xlrd...")
try:
    xl = pd.ExcelFile(file, engine="xlrd")
    print("Success with xlrd. Sheets:", xl.sheet_names)
except Exception as e:
    print("Failed with xlrd:", e)
