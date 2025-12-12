import struct, csv, os

file_path = "input/20250907-150827_Rtk.fmnav"
output_dir = "output_experiments2"
os.makedirs(output_dir, exist_ok=True)

candidates = {
    "A_Qiii":  ("<Qiii",  ["timestamp","x_i32","y_i32","z_i32"]),
    "B_QiiiH": ("<QiiiH", ["timestamp","x_i32","y_i32","z_i32","quality_u16"]),
    "C_QIII":  ("<QIII",  ["timestamp","x_u32","y_u32","z_u32"]),
    "D_QhhhH": ("<QhhhH", ["timestamp","x_i16","y_i16","z_i16","quality_u16"]),
    "E_Qfff":  ("<Qfff",  ["timestamp","x_f","y_f","z_f"]),
}

for name, (fmt, headers) in candidates.items():
    rec_size = struct.calcsize(fmt)
    out_csv = os.path.join(output_dir, f"{name}.csv")

    decoded = []
    with open(file_path, "rb") as f:
        while True:
            b = f.read(rec_size)
            if not b or len(b) < rec_size:
                break
            try:
                vals = struct.unpack(fmt, b)
                decoded.append(vals)
            except struct.error:
                break

    with open(out_csv, "w", newline="") as cf:
        writer = csv.writer(cf)
        writer.writerow(headers)
        writer.writerows(decoded[:20000])  # limit sample size

    print(f"✅ {name}: saved {len(decoded):,} rows to {out_csv}")
