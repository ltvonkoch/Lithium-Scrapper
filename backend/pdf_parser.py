import openai
import spacy
import pdfplumber
import pandas as pd

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
    """Uses OpenAI's GPT to extract structured production numbers from text safely."""
    
    # Ensure extracted text is valid before making an API call
    if not text or len(text.strip()) == 0:
        print("⚠️ Warning: Extracted text is empty. Skipping OpenAI API call.")
        return {"Q4 2024 Production": "n/a", "2024 Production": "n/a", "2025 Production": "n/a"}
    
    try:
        print("🧠 Calling OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Extract production figures from this text for Q1 2024, full-year 2024, and 2025."},
                {"role": "user", "content": text}
            ]
        )
        
        if response and response.choices and response.choices[0].message.content:
            return response.choices[0].message.content
        else:
            print("⚠️ Warning: OpenAI API returned an empty response.")
            return {"Q4 2024 Production": "n/a", "2024 Production": "n/a", "2025 Production": "n/a"}
    
    except openai.OpenAIError as e:
        print(f"❌ OpenAI API Error: {e}")
        return {"Q4 2024 Production": "n/a", "2024 Production": "n/a", "2025 Production": "n/a"}
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return {"Q4 2024 Production": "n/a", "2024 Production": "n/a", "2025 Production": "n/a"}

def extract_production_data(pdf_path):
    """Extracts relevant sections from a 6-K report and calls OpenAI for structured data extraction."""
    all_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)

    full_text = "\n".join(all_text)  # Combine all pages
    print(f"🔍 Full Extracted Text (Preview):\n{full_text[:1000]}...\n{'='*40}")

    # Step 1: Filter out legal and irrelevant text
    relevant_text = filter_relevant_text(full_text)
    
    # Step 2: Extract production figures
    extracted_data = extract_numbers_with_gpt(relevant_text)
    
    # Step 3: Save to Excel
    df = pd.DataFrame([extracted_data])
    df.to_excel("output/sigma_lithium_production.xlsx", index=False)
    print("✅ Data saved to output/sigma_lithium_production.xlsx")
    
    return extracted_data
