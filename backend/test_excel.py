from backend.excel_writer import save_to_excel
from backend.pdf_parser import parse_gpt_output_to_dict  # Import the parsing function

# Define the test file path
test_file_path = "backend/test1.txt"

try:
    print(f"📄 Processing {test_file_path}...")

    # Load the test GPT output from file
    with open(test_file_path, "r") as file:
        gpt_output_text = file.read()

    # Parse the text into a dictionary
    parsed_data = parse_gpt_output_to_dict(gpt_output_text)

    # Define the company name (extracted from text or set manually for testing)
    company_name = parsed_data.pop("Company Name", "Test Company")

    # Run the new Excel implementation
    excel_path = save_to_excel(parsed_data, company_name)

    print(f"✅ Successfully processed {test_file_path}. Data saved to: {excel_path}")

except Exception as e:
    print(f"❌ Error processing {test_file_path}: {e}")

print("✅ Test case complete.")
