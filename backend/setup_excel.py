import pandas as pd
import os
from backend.config import OUTPUT_DIR

def initialize_excel_file():
    """Creates a formatted Excel file if it doesn't already exist."""
    excel_path = os.path.join(OUTPUT_DIR, "lithium_production.xlsx")

    # Ensure file does not already exist (run once)
    if os.path.exists(excel_path):
        print(f"✅ Excel file already exists at {excel_path}. No changes made.")
        return

    # Define quarter-end dates & labels
    quarter_dates = pd.date_range(start="2015-03-31", end="2025-12-31", freq='QE') 
    quarter_labels = [f"Q{(i%4)+1}-{year}" for i, year in enumerate(quarter_dates.year)]

    # Define year-end dates & labels
    year_dates = pd.date_range(start="2015-12-31", end="2025-12-31", freq='YE')
    year_labels = [str(year) for year in year_dates.year]

    # Create an empty DataFrame with correct structure
    columns = ["Company"] + quarter_labels + ["Annual Lithium Production (Tonnes)"] + year_labels
    df = pd.DataFrame(columns=columns)

    # Save initial empty DataFrame
    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Lithium Production", header=False, startrow=10)

        workbook = writer.book
        worksheet = writer.sheets["Lithium Production"]

        # Apply formatting
        bold_format = workbook.add_format({"bold": True})

        # Row 1: Empty
        worksheet.write_blank(0, 0, "", workbook.add_format())

        # Row 2: Headers
        worksheet.write("C2", "Quarterly Lithium Production (Tonnes)", bold_format)
        worksheet.write("AV2", "Annual Lithium Production (Tonnes)", bold_format)
        worksheet.write("B4", "Company", bold_format)

        # Row 3: Dates for quarters
        for i, date in enumerate(quarter_dates):
            col_index = i + 2  # Offset to start at Column C
            worksheet.write_datetime(2, col_index, date, workbook.add_format({'num_format': 'mm/dd/yyyy'}))

        # Row 3: Dates for years (starting at AV)
        for i, date in enumerate(year_dates):
            col_index = i + 47  # Offset to start at Column AV
            worksheet.write_datetime(2, col_index, date, workbook.add_format({'num_format': 'mm/dd/yyyy'}))

        # Row 4: Quarter Labels
        for i, label in enumerate(quarter_labels):
            col_index = i + 2  # Offset to start at Column C
            worksheet.write(3, col_index, label)

        # Row 4: Year Labels (starting at AV)
        for i, label in enumerate(year_labels):
            col_index = i + 47  # Offset to start at Column AV
            worksheet.write(3, col_index, label)

        worksheet.set_column("B:B", 25)  # Make Column B wider (Company column)
        worksheet.set_column("C:BF", 11)  # Set all other columns to 70 pixels wide

        writer.close()

    print(f"✅ Excel file successfully initialized at {excel_path}.")

# Run the setup only when executed directly
if __name__ == "__main__":
    initialize_excel_file()
