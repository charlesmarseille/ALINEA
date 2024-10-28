'''
Author: Charles Marseille, 2024
This script processes Sentinel-1 data by performing the following steps:
1. Reads GeoTIFF files and a shapefile containing class information.
2. Computes zonal statistics for each GeoTIFF file based on the shapefile.
3. Aggregates the statistics by class and saves the results.
4. Visualizes the statistics using boxplots.

Usage:
    python get_stats_from_s1_processed.py
'''

import geopandas as gpd
import rasterio
import rasterio.mask
from rasterstats import zonal_stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from glob import glob
from tqdm import tqdm
import pickle

fnames = glob('outputs/gozdjrt/python_graph_orb/*.tif')
all_grouped_stats = []
shapefile_path = 'shapefiles_classes/Prediction_fine_gozdjrt_corrig.shp'
gdf = gpd.read_file(shapefile_path)

all_stats = []

for tiff_path in tqdm(fnames):
    with rasterio.open(tiff_path) as src:
        transform = src.transform
        array = src.read(1)
        crs = src.crs
        nodata = src.nodata

    stats = ["mean", "min", "max", "sum", "std", "median", "count", "range", "percentile_25", "percentile_50", "percentile_75"]
    s1 = zonal_stats(gdf.to_crs(crs).geometry, array, affine=transform, stats=stats, nodata=np.nan)
    df_stats = pd.DataFrame(s1)
    gdf_combined = pd.concat([gdf.reset_index(drop=True), df_stats], axis=1)
    all_stats.append(gdf_combined)


    classes = gdf["CLASSE"].unique()
    grouped_stats = gdf_combined.groupby('CLASSE').agg({
        'mean': 'mean',
        'min': 'min',
        'max': 'max',
        'sum': 'sum',
        'std': 'std',
        'median': 'median',
        'percentile_25': lambda x: np.percentile(x, 25),
        'percentile_50': lambda x: np.percentile(x, 50),
        'percentile_75': lambda x: np.percentile(x, 75),
    }).reset_index()
    
    grouped_stats['fname'] = tiff_path
    all_grouped_stats.append(grouped_stats)



final_df = pd.concat(all_grouped_stats, ignore_index=True)

# Save all_grouped_stats list to a file
with open('all_grouped_stats.pkl', 'wb') as f:
    pickle.dump(all_grouped_stats, f)

# Read the all_grouped_stats list from the file
with open('all_grouped_stats.pkl', 'rb') as f:
    all_grouped_stats = pickle.load(f)




ncols = 4
nrows = (len(all_grouped_stats) + ncols - 1) // ncols  # Calculate the number of rows needed
fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 4 * nrows), dpi=180, sharex=True, sharey=True)
axes = axes.flatten()  # Flatten the axes array for easy iteration

for ax, stats in zip(axes, all_grouped_stats):
    stats.boxplot(column='mean', by='CLASSE', grid=False, ax=ax)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(axis='x', rotation=45)
    ax.set_title(stats['fname'].iloc[0][-49:-40])  # Use the fname value for each subtitle

# Hide any unused subplots
for ax in axes[len(all_grouped_stats):]:
    ax.axis('off')

plt.suptitle('')  # Suppress the default title to avoid overlap
plt.tight_layout()
plt.show()
