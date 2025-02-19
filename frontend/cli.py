from backend.scraper import download_latest_6k
from backend.pdf_parser import extract_production_data

def main():
    """Main function to run the lithium production data extraction pipeline."""
    pdf_path, company_name = download_latest_6k()
    
    if pdf_path and company_name:
        extract_production_data(pdf_path, company_name)
    else:
        print("❌ Failed to download or process the 6-K filing.")

if __name__ == "__main__":
    main()
