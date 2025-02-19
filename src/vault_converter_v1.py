import json
import sys
""" Convert vault from verson 0 to version 1 """

def convert_vault(input_file, output_file):
    # Read the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Add "icon":null to each entry
    for entry in data:
        entry["icon"] = None

    # Create the new format structure
    new_format = {
        "vault": {
            "version": 1,
            "entries": data
        }
    }

    # Write the new format to the output file
    with open(output_file, 'w') as f:
        json.dump(new_format, f, indent=2)

    print(f"Successfully converted {input_file} to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python vault_converter_v1.py input.json output.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        convert_vault(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)