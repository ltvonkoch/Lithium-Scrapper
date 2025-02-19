import openai
import spacy
import pdfplumber
import re
from backend.excel_writer import save_to_excel  # Ensure we use the updated excel_writer
from backend.scraper import SIGMA_LITHIUM_URL
from urllib.parse import urlparse

# Load SpaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize OpenAI client
client = openai.OpenAI()

def filter_relevant_text(text):

    """Uses OpenAI to extract only the relevant business and production sections from a long document."""
    try:
        print("🧠 Filtering Relevant Sections Using GPT...")

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Identify and extract the relevant section containing production figures from the following document. Remove legal disclaimers, forward-looking statements, and regulatory notices."},
                {"role": "user", "content": text}
            ]
        )

        if response and response.choices and response.choices[0].message.content:
            return response.choices[0].message.content
        else:
            print("⚠️ Warning: OpenAI API returned an empty response while filtering text.")
            return text  # Return full text if filtering fails

    except openai.OpenAIError as e:
        print(f"❌ OpenAI API Error: {e}")
        return text  # Fail gracefully and return unfiltered text

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return text  # Return unfiltered text on error

def extract_numbers_with_gpt(text):
    """
    Uses OpenAI's GPT to extract structured production numbers from text 
    in a custom format using a few-shot learning approach.
    """

    # Ensure extracted text is valid before making an API call
    if not text or len(text.strip()) == 0:
        print("⚠️ Warning: Extracted text is empty. Skipping OpenAI API call.")
        return {}

    try:
        print("🧠 Calling OpenAI API with few-shot learning...")

        # Example input-output pairs to nudge GPT
        few_shot_path = "backend/few_shot_example.txt"
        with open(few_shot_path, "r") as file:
            few_shot_example = file.read()
        
        prompt = f"""
{few_shot_example}

Now, extract production figures from the following text in the exact same format. 
If any quarters or years are missing, omit them from the response.

{text}
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that reads text about lithium production "
                        "and outputs data in a specific format: \n\n"
                        "Company Name: <Name>\n\n"
                        "Quarters:\nQ1-YYYY: <amount>\n...\n\n"
                        "Years:\nYYYY: <amount>\n...\n\n"
                        "Do not add extra commentary."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        if response and response.choices and response.choices[0].message.content:
            structured_output = response.choices[0].message.content.strip()
            return structured_output
        else:
            print("⚠️ Warning: OpenAI API returned an empty response.")
            return {}

    except openai.OpenAIError as e:
        print(f"❌ OpenAI API Error: {e}")
        return {}
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return {}


def extract_company_name_from_url(url):
    """Extracts the company name from the URL instead of using OpenAI."""
    print("🔎 Extracting Company Name from URL...")

    try:
        parsed_url = urlparse(url)
        domain_parts = parsed_url.netloc.split(".")  # Split domain into parts

        # Use the second-level domain as company name (e.g., "sigmalithiumresources" from "ir.sigmalithiumresources.com")
        if len(domain_parts) > 2:
            company_name = domain_parts[-3].replace("-", " ").title()  # Clean formatting
        else:
            company_name = domain_parts[0].replace("-", " ").title()

        print(f"✅ Extracted Company Name: {company_name}")
        return company_name

    except Exception as e:
        print(f"❌ Error extracting company name: {e}")
        return parsed_url
    

def parse_gpt_output_to_dict(gpt_output: str) -> dict:

    result = {}

    # 1️⃣ Extract company name
    match_company = re.search(r"Company\s+Name:\s*(.+)", gpt_output)
    if match_company:
        result["Company Name"] = match_company.group(1).strip()

    # 2️⃣ Extract Quarters
    # Find lines like `Q4-2024: 75,000 tonnes`
    quarter_lines = re.findall(r"(Q[1-4]-\d{4}):\s*([0-9,]+\s*\w+)", gpt_output)
    for (quarter, amount) in quarter_lines:
        result[quarter] = amount.strip()

    # 3️⃣ Extract Years
    # Find lines like `2024: 240,000 tonnes`
    year_lines = re.findall(r"(\d{4}):\s*([0-9,]+\s*\w+)", gpt_output)
    for (year, amount) in year_lines:
        result[year] = amount.strip()

    return result



def extract_production_data(pdf_path, company_name):
    """Extracts relevant sections from a 6-K report and calls OpenAI for structured data extraction."""
    all_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)

    full_text = "\n".join(all_text)  # Combine all pages
    print(f"🔍 Full Extracted Text (Preview):\n{full_text[:1000]}...\n{'='*40}")

    # Step 1: Extract company name
    company_name = extract_company_name_from_url(SIGMA_LITHIUM_URL)

    # Step 2: Filter out legal and irrelevant text
    relevant_text = filter_relevant_text(full_text)
    
    # Step 3: Extract production figures
    preprocessed_data = extract_numbers_with_gpt(relevant_text)
    
    # Step 4: Format production figures
    extracted_data = parse_gpt_output_to_dict(preprocessed_data)

    # Step 5: Save to Excel
    save_to_excel(extracted_data, company_name)

    print(f"✅ Data saved for {company_name}")
    return extracted_data
