
from backend.scraper import download_latest_6k
from backend.pdf_parser import extract_production_data
from backend.excel_writer import save_to_excel

def main():
    pdf_path = download_latest_6k()
    if pdf_path:
        data = extract_production_data(pdf_path)
        save_to_excel(data)

if __name__ == "__main__":
    main()