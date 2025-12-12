import os
import re

# Path to your file
input_file = "20250907-150827_Rtk.dfnav"

def extract_readable_strings(input_file, min_length=3):
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}.txt"

    with open(input_file, "rb") as f:
        data = f.read()

    # Extract printable ASCII sequences of length >= min_length
    pattern = re.compile(rb"[ -~]{%d,}" % min_length)
    matches = pattern.findall(data)

    # Decode each byte sequence safely to UTF-8 text
    # try different encoding
    readable_strings = [m.decode("utf-8", errors="ignore") for m in matches]

    # Save to .txt
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("\n".join(readable_strings))

    print(f"✅ Decoded text saved as: {output_file}")

# Run
extract_readable_strings(input_file)
