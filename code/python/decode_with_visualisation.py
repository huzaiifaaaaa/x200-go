import struct, csv, os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# =====================================================
# Configuration
# =====================================================
file_path = "input/20250907-150827_Rtk.fmnav"
output_dir = "output_experiments_visual"
os.makedirs(output_dir, exist_ok=True)

# Candidate binary layouts
candidates = {
    "A_Qiii":  ("<Qiii",  ["timestamp","x_i32","y_i32","z_i32"]),
    "B_QiiiH": ("<QiiiH", ["timestamp","x_i32","y_i32","z_i32","quality_u16"]),
    "C_QIII":  ("<QIII",  ["timestamp","x_u32","y_u32","z_u32"]),
    "D_QhhhH": ("<QhhhH", ["timestamp","x_i16","y_i16","z_i16","quality_u16"]),
    "E_Qfff":  ("<Qfff",  ["timestamp","x_f","y_f","z_f"]),
}

MAX_RECORDS = 50000  # sample limit for speed/plot clarity


# =====================================================
# Decoder
# =====================================================
def decode_file(fmt, headers):
    rec_size = struct.calcsize(fmt)
    decoded = []
    with open(file_path, "rb") as f:
        while len(decoded) < MAX_RECORDS:
            b = f.read(rec_size)
            if not b or len(b) < rec_size:
                break
            try:
                vals = struct.unpack(fmt, b)
                decoded.append(vals)
            except struct.error:
                break
    return np.array(decoded), headers


# =====================================================
# Analyzer
# =====================================================
def analyze_variant(name, arr, headers):
    out_csv = os.path.join(output_dir, f"{name}.csv")
    np.savetxt(out_csv, arr, delimiter=",", header=",".join(headers), comments="", fmt="%s")
    print(f"✅ {name}: saved {arr.shape[0]:,} rows to {out_csv}")

    # ---- Timestamp analysis
    if arr.shape[1] >= 1:
        timestamps = arr[:, 0].astype(np.float64)
        diffs = np.diff(timestamps)
        plt.figure(figsize=(6,3))
        plt.plot(diffs[:2000])
        plt.title(f"Timestamp deltas — {name}")
        plt.xlabel("Record")
        plt.ylabel("Δ timestamp")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{name}_timestamps.png"))
        plt.close()

    # ---- Coordinate histograms (safe handling)
    cols = min(3, arr.shape[1]-1)
    plt.figure(figsize=(10,3))
    for i in range(cols):
        data = arr[:, i+1].astype(np.float64)
        data = data[np.isfinite(data)]           # remove NaN/inf
        if len(data) == 0:
            continue
        # limit to 99th percentile to avoid absurd ranges
        lo, hi = np.percentile(data, [0.1, 99.9])
        data = np.clip(data, lo, hi)
        plt.subplot(1, cols, i+1)
        plt.hist(data, bins=100, color="steelblue", alpha=0.7)
        plt.title(f"{headers[i+1]}")
        plt.tight_layout()
    plt.suptitle(f"Coordinate distributions — {name}", y=1.05, fontsize=10)
    plt.savefig(os.path.join(output_dir, f"{name}_hist.png"), bbox_inches="tight")
    plt.close()

    # ---- 3D scatter (if there are at least 3 coords)
    if arr.shape[1] >= 4:
        fig = plt.figure(figsize=(6,5))
        ax = fig.add_subplot(111, projection="3d")
        x, y, z = arr[:,1], arr[:,2], arr[:,3]
        finite_mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
        x, y, z = x[finite_mask], y[finite_mask], z[finite_mask]
        if len(x) == 0:
            return
        step = max(1, len(x)//20000)
        ax.scatter(x[::step], y[::step], z[::step], s=1, alpha=0.6)
        ax.set_xlabel(headers[1])
        ax.set_ylabel(headers[2])
        ax.set_zlabel(headers[3])
        plt.title(f"3D Scatter — {name}")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{name}_3dscatter.png"), dpi=200)
        plt.close()


# =====================================================
# Main Execution
# =====================================================
for name, (fmt, headers) in candidates.items():
    print(f"\n🔹 Trying {name}: {fmt}")
    arr, hdr = decode_file(fmt, headers)
    if len(arr) == 0:
        print(f"⚠️  {name}: no records decoded.")
        continue
    analyze_variant(name, arr, hdr)

print("\n🎯 All decoding variants tested and plotted.")
print(f"📁 Check results in: {output_dir}")
