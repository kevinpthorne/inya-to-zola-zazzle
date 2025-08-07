import pandas as pd
import numpy as np
import argparse # Import the library for CLI arguments
import re

def read_names(filepath):
    """Reads names from a file into a set, stripping whitespace and ignoring empty lines."""
    with open(filepath) as f:
        return {line.strip() for line in f if line.strip()}

known_dupes = read_names('known-drops.txt')
drop_emails = read_names('known-drop-emails.txt')
drop_mail = read_names('known-no-mail.txt')

def map_csv_data(input_file, output_file):
    """
    Reads a CSV file, maps its columns to a new format, and saves the result.

    Args:
        input_file (str): The path to the source CSV file.
        output_file (str): The path where the output CSV file will be saved.
    """
    try:
        # 1. Read the source CSV file into a pandas DataFrame
        # Using the provided command-line argument for the input file
        print(f"🔄 Reading data from '{input_file}'...")
        df = pd.read_csv(input_file)

        # 2. Create a new DataFrame to hold the mapped data
        # This avoids modifying the original data and makes the mapping clear.
        df_output = pd.DataFrame()

        # 3. Perform the column mapping
        # Note: .get(col, None) safely handles cases where a column might be missing
        # from the input file, preventing errors.

        # --- Column Mapping Logic ---

        # Name: Mapped from 'full_name'
        df_output['Full Name'] = df.get('full_name', None)

        # standardize multiple names
        df_output = df_output[~df_output['Full Name'].isin(known_dupes)]
        df_output = df_output[~df_output['Full Name'].isin(drop_mail)]
        df_output['Full Name'] = df_output['Full Name'].str.replace(' and ', ' & ')
        
        # Direct Mappings
        # df_output['Email Address'] = df.get('email_address', None).replace(drop_emails, '')
        # df_output['Phone Number'] = df.get('phone_number', None)
        df_output['Country'] = df.get('country', None)
        df_output['Company'] = None
        
        # if country is null, make USA
        df_output.loc[(df_output['Country'].isnull()), 'Country'] = 'USA'
        df_output.loc[(df_output['Country'] == "Us"), 'Country'] = 'USA'

        df_output['Address 1'] = df.get('address_line_1', None).str.title()
        df_output['Address 2 (e.g. Unit #)'] = df.get('address_line_2', None).str.title()
        df_output['Address 3'] = None
        df_output['City'] = df.get('city', None).str.title()
        df_output['State'] = df.get('state', None)
        df_output['Zip Code'] = df.get('postal_code', None)
        df_output['Phone Number'] = None
        df_output['Email'] = None

        # Drop duplicate Address 1 lines
        # Create temporary columns with uppercase values of 'Address 1' and 'City'
        df_output['Address 1 upper'] = df_output['Address 1'].str.upper()
        df_output['City upper'] = df_output['City'].str.upper()
        df_output['Full Name upper'] = df_output['Full Name'].str.upper()

        # Drop duplicates based on the temporary uppercase columns
        df_output = df_output.drop_duplicates(subset=['Full Name upper', 'Address 1 upper', 'City upper'], keep='first')
        # df_output['dupe'] = df_output.duplicated(subset=['Address 1 upper', 'City upper'], keep=False)
        # df_output = df_output[df_output['dupe']]
        # df_output = df_output.sort_values(by='Address 1')

        # # Drop the temporary columns
        df_output = df_output.drop(columns=['Full Name upper',  'Address 1 upper', 'City upper'])

        # 4. Save the mapped data to a new CSV file
        # Using the provided command-line argument for the output file
        # `index=False` prevents pandas from writing the DataFrame index as a column.
        df_output.to_csv(output_file, index=False, encoding='utf-8')

        print(f"✅ Successfully mapped data to '{output_file}'")
        print("\n--- First 5 rows of mapped data ---")
        print(df_output.head())

    except FileNotFoundError:
        print(f"❌ Error: The file '{input_file}' was not found.")
        print("Please make sure you have provided the correct path to the input file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Function to handle the special splitting logic
def split_shared_lastname(name):
    """
    Splits names like "First1 & First2 Last" into "First1 Last" and "First2 Last".
    Falls back to a simple split for names like "Item 1 & Item 2".
    """
    try:
        # Split the name into two main parts around the ampersand
        # e.g., "John & Jane Doe" -> ["John", "Jane Doe"]
        person1_part, person2_part = re.split(r'\s*&\s*', name, 1)

        # Split the second part by spaces to find the last name
        # e.g., "Jane Doe" -> ["Jane", "Doe"]
        person2_words = person2_part.strip().split(' ')

        # If the second part has more than one word, assume a shared last name
        if len(person2_words) > 1:
            last_name = person2_words[-1]
            person2_first_name = " ".join(person2_words[:-1])

            full_name1 = f"{person1_part.strip()} {last_name}"
            full_name2 = f"{person2_first_name} {last_name}"
            return pd.Series([full_name1, full_name2])
        else:
            # Fallback for simple pairs like "Salt & Pepper"
            return pd.Series([person1_part.strip(), person2_part.strip()])
    except (ValueError, IndexError):
        # Handle cases where the split doesn't work as expected
        return pd.Series([pd.NA, pd.NA])

# This is the main entry point when the script is run from the command line
if __name__ == "__main__":
    # 1. Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Maps columns from an input CSV to a specified output format."
    )

    # 2. Define the command-line arguments
    parser.add_argument(
        "input_file",
        help="The path to the source CSV file to be processed."
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_file",
        default="zazzle.csv",
        help="The path for the output file. Defaults to 'zazzle.csv' in the current directory."
    )

    # 3. Parse the arguments provided by the user
    args = parser.parse_args()

    # 4. Call the main function with the user-provided file paths
    map_csv_data(args.input_file, args.output_file)
