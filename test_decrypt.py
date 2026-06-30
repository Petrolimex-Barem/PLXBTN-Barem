import msoffcrypto
import io
import pandas as pd

file = "CHXD 31_BAREM_UPDATE 2023.xls"
decrypted = io.BytesIO()

try:
    with open(file, "rb") as f:
        office_file = msoffcrypto.OfficeFile(f)
        # Try default passwords. VelvetSweatshop is standard.
        office_file.load_key(password="VelvetSweatshop")
        office_file.decrypt(decrypted)
        
    decrypted.seek(0)
    # Check if pandas can read it now
    xl = pd.ExcelFile(decrypted, engine="calamine")
    print("Success decrypting with VelvetSweatshop! Sheets:", xl.sheet_names)
except Exception as e:
    print("Failed to decrypt with VelvetSweatshop:", e)
