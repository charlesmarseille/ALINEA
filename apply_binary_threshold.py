import rasterio
import numpy as np
import sys
import argparse

def create_binary_mask(input_tif, threshold):
    # Open the input TIFF file
    with rasterio.open(input_tif) as src:
        # Read the first band
        band = src.read(1)
        
        # Create a binary mask where data is above the threshold
        binary_mask = (band > threshold).astype(np.uint8)
        
        # Define the metadata for the output file
        meta = src.meta.copy()
        meta.update(dtype=rasterio.uint8, count=1)
        
        # Write the binary mask to the output TIFF file
        with rasterio.open(f'{input_tif[:-4]}_binary_threshold_{threshold}.tif', 'w', **meta) as dst:
            dst.write(binary_mask, 1)
            print(f'{input_tif[:-4]}_binary_threshold_{threshold}.tif')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a binary mask from a TIFF file based on a threshold.")
    parser.add_argument('--input', required=True, help="Path to the input TIFF file")
    parser.add_argument('--threshold', required=True, type=float, help="Threshold value to create the binary mask")
    
    args = parser.parse_args()
    
    create_binary_mask(args.input, args.threshold)