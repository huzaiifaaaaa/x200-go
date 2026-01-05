
"""
This script reads raw binary data from an HP IMU (.fmimr) file, skips the header,
splits the payload into fixed-size blocks, and attempts to interpret each block's
bytes as various data types (int16, uint16, int32, uint32, float32, float16) in
both little-endian and big-endian formats. For each possible byte offset within
a block, it plots the interpreted values across multiple blocks to help identify
the correct data structure and field alignment.
"""

import struct
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------
# Configuration
# -----------------------------
FILE_PATH = ""  # Input file path
BLOCK_SIZE = 33                              # Size of one data block in bytes
HEADER_SIZE = 1024                           # Header size in bytes to skip
NUM_BLOCKS_TO_PLOT = 111                     # Number of blocks to visualize

# -----------------------------
# Load and slice raw data
# -----------------------------
with open(FILE_PATH, "rb") as f:
    file_bytes = f.read()

# Remove header; keep only payload
payload = file_bytes[HEADER_SIZE:]

# Split payload into fixed-size blocks
all_blocks = [payload[i:i + BLOCK_SIZE] for i in range(0, len(payload), BLOCK_SIZE)]

# Keep only full blocks and take first N blocks
blocks = [blk for blk in all_blocks if len(blk) == BLOCK_SIZE][:NUM_BLOCKS_TO_PLOT]

# -----------------------------
# Data type hypotheses to test
# -----------------------------
DATA_TYPES = [
    ("h", 2, "int16"),
    ("H", 2, "uint16"),
    ("i", 4, "int32"),
    ("I", 4, "uint32"),
    ("f", 4, "float32"),
    ("e", 2, "float16"),  # 'e' = float16 (Python 3.6+)
]

ENDIANNESS = {"LE": "<", "BE": ">"}

# -----------------------------
# Sweep offsets and visualize
# -----------------------------
for fmt_code, byte_width, dtype_name in DATA_TYPES:
    for endian_label, endian_prefix in ENDIANNESS.items():
        print(f"\n=== {dtype_name} {endian_label} ===")

        max_offset_exclusive = BLOCK_SIZE - byte_width + 1

        # Plot 10 offsets per figure
        for start_offset in range(0, max_offset_exclusive, 10):
            stop_offset = min(start_offset + 10, max_offset_exclusive)

            num_rows = stop_offset - start_offset
            fig, axes = plt.subplots(num_rows, 1, figsize=(10, 2 * num_rows), sharex=True)
            if num_rows == 1:
                axes = [axes]

            for ax_idx, offset in enumerate(range(start_offset, stop_offset)):
                values = []
                for blk in blocks:
                    if offset + byte_width <= len(blk):
                        try:
                            value = struct.unpack(endian_prefix + fmt_code, blk[offset:offset + byte_width])[0]
                        except Exception:
                            value = np.nan
                        values.append(value)

                axes[ax_idx].plot(values, lw=0.8)
                axes[ax_idx].set_title(f"{dtype_name} {endian_label} @ offset {offset}")
                axes[ax_idx].grid(True)

            fig.suptitle(
                f"Block size={BLOCK_SIZE} | Header={HEADER_SIZE} | Blocks plotted={NUM_BLOCKS_TO_PLOT}",
                y=1.02, fontsize=11
            )
            plt.tight_layout()
            plt.show()

