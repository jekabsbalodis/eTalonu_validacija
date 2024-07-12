import random
import sys
import os


def process_file(filepath, encoding):
    try:
        # Read all lines from the file
        with open(filepath, 'r', encoding=encoding) as file:
            lines = file.readlines()

        if len(lines) <= 1:
            print(f"{filepath} has 1 or fewer lines. No changes made.")
            return

        # Separate the header (first row) from the rest
        header = lines[0]
        body = lines[1:]

        # Randomly select 100 lines from the body
        selected_lines = random.sample(body, min(100, len(body)))

        # Combine the header with the selected lines
        result = [header] + selected_lines

        # Write the header and selected lines back to the file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.writelines(result)

        print(f"Successfully reduced {filepath} to {
              len(result)} rows (1 header + {len(selected_lines)} random rows).")

    except Exception as e:
        print(f"An error occurred while processing {filepath}: {e}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python random_rows.py <folder_path> <encoding>")
        sys.exit(1)

    folder_path = sys.argv[1]
    encoding = sys.argv[2]

    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        sys.exit(1)

    # Get all .txt files in the specified directory
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

    if not txt_files:
        print(f"No .txt files found in {folder_path}.")
        sys.exit(1)

    # Process each .txt file
    for filename in txt_files:
        filepath = os.path.join(folder_path, filename)
        process_file(filepath, encoding)

    print(f"Processed {len(txt_files)} .txt files.")


if __name__ == "__main__":
    main()
