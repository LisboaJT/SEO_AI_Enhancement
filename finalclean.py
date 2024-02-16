import pandas as pd
from config import CSV_OUTPUT_PATH_QC_LAST, CSV_OUTPUT_PATH_QC_CLEAN

# Specify the path to your input CSV file and the output file
input_csv_path = CSV_OUTPUT_PATH_QC_LAST  # Update this path
output_csv_path = CSV_OUTPUT_PATH_QC_CLEAN  # Update this path

# Load the data from CSV
df = pd.read_csv(input_csv_path)

# Specify the fields you want to conditionally strip quotation marks from
fields_to_strip = ['meta_description', 'seo_title']

def conditional_strip(value):
    """Strip quotation marks only if they are the first or last character."""
    if isinstance(value, str):
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
    return value

# Loop through each field and apply the conditional strip function
for field in fields_to_strip:
    if field in df.columns:
        df[field] = df[field].apply(conditional_strip)
    else:
        print(f"Warning: '{field}' does not exist in the DataFrame.")

# Write the modified DataFrame to a new CSV file
df.to_csv(output_csv_path, index=False)

print(f"Data processed and saved to '{output_csv_path}'.")