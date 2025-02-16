import pandas as pd
import os
from backend.config import OUTPUT_DIR


def save_to_excel(data):
    """Saves extracted production data into an Excel file."""
    df = pd.DataFrame([data])
    excel_path = os.path.join(OUTPUT_DIR, "sigma_lithium_production.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"Data saved to {excel_path}")
    return excel_path