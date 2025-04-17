import pgeocode
import pandas as pd
import re
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize GeoDistance for UK
geo = pgeocode.GeoDistance("gb")

# Function to validate postcode format using regex
def is_valid_postcode(postcode):
    full_pattern = r"^[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}$"
    short_pattern = r"^[A-Z]{1,2}[0-9][0-9A-Z]?$"
    return bool(re.match(full_pattern, postcode) or re.match(short_pattern, postcode))

# Function to calculate distance between two postcodes
def get_distance_between_postcodes(from_postcode, to_postcode):
    from_postcode = from_postcode.strip().upper()
    to_postcode = to_postcode.strip().upper()

    if not (is_valid_postcode(from_postcode) and is_valid_postcode(to_postcode)):
        return "Invalid postcode"

    distance = geo.query_postal_code(from_postcode, to_postcode)

    if pd.isna(distance):
        return "Invalid postcode"

    distance_miles = distance * 0.621371
    return round(distance_miles, 2)

# Function to process CSV and calculate distances
def calculate_distances_from_csv(input_file, source_col_idx, dest_col_idx):
    try:
        # Read input CSV
        if not os.path.exists(input_file):
            logging.error(f"Input file {input_file} not found")
            return None
        
        df = pd.read_csv(input_file)
        logging.info(f"Loaded input CSV with {len(df)} rows")

        # Validate column indices
        if source_col_idx >= len(df.columns) or dest_col_idx >= len(df.columns):
            logging.error(f"Column indices {source_col_idx} or {dest_col_idx} out of range")
            return None

        # Map indices to column names
        source_col = df.columns[source_col_idx]
        dest_col = df.columns[dest_col_idx]

        # Calculate distances
        def calculate_distance(row):
            if pd.notna(row[source_col]) and pd.notna(row[dest_col]):
                return get_distance_between_postcodes(row[source_col], row[dest_col])
            return "Invalid postcode"

        df['distance_miles'] = df.apply(calculate_distance, axis=1)
        return df

    except Exception as e:
        logging.error(f"Error processing CSV: {e}")
        return None

# Main function
def main():
    # Define input and output paths
    input_folder = "input"
    output_folder = "output"
    input_file = os.path.join(input_folder, "postcodes.csv")
    output_file = os.path.join(output_folder, "postcode_distances.csv")

    # Create folders if they don't exist
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    # Prompt user for column indices
    print("Available columns in CSV:")
    df = pd.read_csv(input_file)
    for idx, col in enumerate(df.columns):
        print(f"{idx}: {col}")
    
    try:
        print("Enter the column number for source postcode (e.g., 3):")
        source_col_idx = int(input().strip())
        print("Enter the column number for destination postcode (e.g., 4):")
        dest_col_idx = int(input().strip())
    except ValueError:
        print("Invalid input. Please enter numbers.")
        return

    # Process CSV
    df = calculate_distances_from_csv(input_file, source_col_idx, dest_col_idx)
    if df is not None:
        # Save output
        df.to_csv(output_file, index=False)
        logging.info(f"Output saved to {output_file}")
        print(f"Output DataFrame:\n{df.head()}")
    else:
        print("Failed to process CSV. Check logs for details.")

if __name__ == "__main__":
    main()