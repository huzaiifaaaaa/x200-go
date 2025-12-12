import rasterio
import matplotlib.pyplot as plt
import numpy as np

# Path to your raster file
raster_path = "20250907-150827_Rtk"

# Open the raster file
with rasterio.open(raster_path) as dataset:
    # Read the raster bands into numpy arrays
    # If you have multiple bands, you can loop over them
    band1 = dataset.read(1)  # Reads the first band
    band_count = dataset.count
    print(f"Number of bands: {band_count}")
    
    # Metadata of the raster
    print("CRS:", dataset.crs)
    print("Width x Height:", dataset.width, "x", dataset.height)
    print("Bounds:", dataset.bounds)
    
    # Optionally, read all bands at once
    all_bands = dataset.read()  # shape = (bands, rows, cols)

# Example: visualize the first band
plt.imshow(band1, cmap='gray')
plt.title("Raster Band 1")
plt.colorbar()
plt.show()
