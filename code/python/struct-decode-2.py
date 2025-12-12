import struct
import csv
import os
import sys
import time
import pandas as pd

# =====================================================
# Configuration
# =====================================================
input_file = "input/20250907-150827_Rtk.fmnav"   # <--- Path to your .fmnav file
output_folder = "output"
max_records = 1000                              # Limit to avoid huge outputs
os.makedirs(output_folder, exist_ok=True)


# =====================================================
# Helper: Try a decoding format
# =====================================================
def try_decode(file_path, record_format, max_records=20000):
    record_size = struct.calcsize(record_format)
    decoded = []
    total_records = 0
    with open(file_path, "rb") as f:
        while total_records < max_records:
            chunk = f.read(record_size)
            if not chunk or len(chunk) < record_size:
                break
            try:
                values = struct.unpack(record_format, chunk)
                decoded.append(values)
                total_records += 1
            except struct.error:
                break
    return decoded


# =====================================================
# Candidate binary layouts to test
# =====================================================
candidates = {
    "A_<Qffff": ("<Qffff", ['timestamp', 'x', 'y', 'z', 'quality']),
    "B_<Qddd f": ("<Qddd f", ['timestamp', 'lat', 'lon', 'alt', 'quality']),
    "C_>Qffff": (">Qffff", ['timestamp', 'x', 'y', 'z', 'quality']),
    "D_<Qiii f": ("<Qiii f", ['timestamp', 'x_int', 'y_int', 'z_int', 'quality']),
    "E_<Qfff": ("<Qfff", ['timestamp', 'x', 'y', 'z']),
    "F_<Qdddf": ("<Qdddf", ['timestamp', 'lat', 'lon', 'alt', 'quality']),
    "G_<Iffff": ("<Iffff", ['timestamp', 'x', 'y', 'z', 'quality']),
    "H_<Qfffff": ("<Qfffff", ['timestamp', 'x', 'y', 'z', 'extra']),
    "I_>Qfff": (">Qfff", ['timestamp', 'x', 'y', 'z']),
    "J_<QfffI": ("<QfffI", ['timestamp', 'x', 'y', 'z', 'id']),
}


# =====================================================
# Main logic
# =====================================================
def run_experiments():
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    results_summary = []
    print(f"🔍 Starting multi-format decoding on {os.path.basename(input_file)}\n")

    for name, (fmt, headers) in candidates.items():
        print(f"🔹 Trying {name}: {fmt}")
        start = time.time()
        decoded = try_decode(input_file, fmt, max_records=max_records)
        elapsed = time.time() - start
        csv_path = os.path.join(output_folder, f"decoded_{name}.csv")

        # Save subset to CSV
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(decoded[:5000])  # only first few thousand

        n = len(decoded)
        sample = decoded[0] if decoded else "N/A"
        print(f"   → {n:,} records | sample: {sample} | {elapsed:.2f}s\n")

        results_summary.append({
            "Method": name,
            "Format": fmt,
            "Records": n,
            "Sample": sample,
            "File": csv_path
        })

    print("✅ All decoding attempts completed.\n")
    summary_path = os.path.join(output_folder, "summary.csv")
    pd.DataFrame(results_summary).to_csv(summary_path, index=False)
    print(f"📊 Summary saved to {summary_path}")


if __name__ == "__main__":
    run_experiments()
