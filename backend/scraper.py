from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import time
import os
import requests
from backend.config import OUTPUT_DIR

SIGMA_LITHIUM_URL = "https://ir.sigmalithiumresources.com/#filings"

def download_latest_6k():
    """Uses Selenium to find and download the latest 6-K filing from Sigma Lithium's website."""
    
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(SIGMA_LITHIUM_URL)
        time.sleep(5)  # Allow time for JavaScript to load

        # Find the latest 6-K row
        filings = driver.find_elements(By.XPATH, "//tr[contains(., '6-K')]")
        
        if not filings:
            print("6-K filing not found.")
            return None

        latest_filing = filings[0]  # First row should be the latest
        
        try:
            company_name = driver.find_element(By.XPATH, "//h1").text
        except NoSuchElementException:
            print("⚠️ Warning: Could not find company name, defaulting to URL.")
            company_name = SIGMA_LITHIUM_URL

        # Find the PDF download link inside the row
        pdf_link_element = latest_filing.find_element(By.XPATH, ".//a[contains(@href, '.pdf')]")
        pdf_url = pdf_link_element.get_attribute("href")

        if not pdf_url:
            print("PDF link not found in the latest 6-K filing.")
            return None

        pdf_path = os.path.join(OUTPUT_DIR, "sigma_lithium_6k.pdf")
        
        # Download the PDF
        response = requests.get(pdf_url)
        with open(pdf_path, "wb") as file:
            file.write(response.content)

        print(f"Downloaded latest 6-K to {pdf_path}")
        return pdf_path, company_name

    finally:
        driver.quit()  # Close the browser

def setup_webdriver():
    """Ensures ChromeDriver matches the installed Chrome version."""
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Automatically install the matching ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver
