'''
Author: Charles Marseille, 2024
This script processes Sentinel-1 data by performing the following steps:
1. Generates a WKT polygon from the shapefile.
2. Updates XML templates for processing and conversion.
3. Executes SNAP gpt commands to process Sentinel-1 data and convert to TIFF format.
4. Merges TIFF files of the same dates.

The input folder must have the shapefile and the Sentinel-1 data in .SAFE.zip format.

Usage:
    python process_sentinel.py --input_folder <path_to_input_folder>
'''


import os
import subprocess
import zipfile
import requests
import geopandas as gpd
import sys
import argparse
import time
import rasterio
from tqdm import tqdm
from datetime import datetime as dt
from osgeo import ogr
from shapely.geometry import Polygon
from shapely import wkt
from rasterio.merge import merge
from rasterio.plot import show
from glob import glob

# gpt_path = '/vscode/esa-snap/bin/gpt'

def print_ascii_art():
    art = """
**************************************************************************************
       _____ _   _____    ____                                                    
      / ___// | / /   |  / __ \   ____  _________  ________  ______________  _____
      \__ \/  |/ / /| | / /_/ /  / __ \/ ___/ __ \/ ___/ _ \/ ___/ ___/ __ \/ ___/
     ___/ / /|  / ___ |/ ____/  / /_/ / /  / /_/ / /__/  __(__  |__  ) /_/ / /    
    /____/_/ |_/_/  |_/_/      / .___/_/   \____/\___/\___/____/____/\____/_/     
                              /_/                                                 

**************************************************************************************                              
    """
    print(art)

def stat_print(mess):
    print(f'''
**************************************************************************************
*
Beginning {mess}...
{now}
*
******************************
    ''')


def merge_tif_files(directory):
    # stat_print("merge tifs")
    files_by_date = {}

    for filename in os.listdir(directory):
        if filename.endswith("_processed.tif"):
            print(f"Processing {filename}")
            date_str = filename[17:25]
            try:
                date = dt.strptime(date_str, '%Y%m%d').date()
            except ValueError:
                print(f"Could not parse date from filename:  {filename}")
                continue

            if date not in files_by_date:
                files_by_date[date] = []
            files_by_date[date].append(os.path.join(directory, filename))

    for date, file_paths in tqdm(files_by_date.items()):
        if len(file_paths) > 1:
            src_files_to_mosaic = []
            for fp in file_paths:
                src = rasterio.open(fp)
                src_files_to_mosaic.append(src)

            mosaic, out_trans = merge(src_files_to_mosaic)

            out_meta = src.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": mosaic.shape[1],
                "width": mosaic.shape[2],
                "transform": out_trans
            })

            merged_filename = os.path.join(directory, f"{date}_merged.tif")
            with rasterio.open(merged_filename, "w", **out_meta) as dest:
                dest.write(mosaic)

            for src in src_files_to_mosaic:
                src.close()


print_ascii_art()

parser = argparse.ArgumentParser(description='Process Sentinel-1 data.')
parser.add_argument('--input_folder', type=str, required=True, help='Path to the input Sentinel-1 data file')
args = parser.parse_args()
parser.print_help()

input_folder = args.input_folder
shapefile_path = glob(input_folder + '/*.shp')

if not os.path.exists(input_folder):
    print(f"File {input_file} does not exist.")
    sys.exit(1)

if len(shapefile_path)>1:
    print(f"Multiple shapefiles found, 1 is required: {shapefile_path}")
    sys.exit(1)

if not os.path.exists(shapefile_path[0]):
    print(f"No shapefile found in folder.")
    sys.exit(1)

for input_file in glob(input_folder + '/*SAFE.zip'):
    wkt_file_path = f'{shapefile_path[0][:-4]}.wkt'
    if not os.path.exists(wkt_file_path):
        gdf = gpd.read_file(shapefile_path[0])
        bounds = gdf.bounds
        minx, miny, maxx, maxy = bounds.minx.min(), bounds.miny.min(), bounds.maxx.max(), bounds.maxy.max()
        polygon = Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)])
        polygon_gdf = gpd.GeoDataFrame(index=[0], crs=gdf.crs, geometry=[polygon])
        print("polygon crs: ", polygon_gdf.crs)
        print("Reprojecting the polygon to the same CRS as the sentinel-1 product")
        polygon_gdf_4326 = polygon_gdf.to_crs(epsg=4326)
        wkt_polygon = wkt.dumps(polygon_gdf_4326.iloc[0].geometry)
        with open(wkt_file_path, 'w') as wkt_file:
            wkt_file.write(wkt_polygon)
        print(f"WKT polygon saved to {wkt_file_path}")
    else:
        with open(wkt_file_path, 'r') as wkt_file:
            wkt_polygon = wkt_file.read()

    subset_orbit_template = 'orb.xml'
    subset_orbit_temp = 'orb_temp.xml'
    output_file = f'{input_file[:-9]}_processed'
    with open(subset_orbit_template, 'r') as file:
        xml_content = file.read()
        new_geo_region = f'<geoRegion>{wkt_polygon}</geoRegion>'
        updated_xml_content = xml_content.replace('<geoRegion/>', new_geo_region).replace('<file>$input</file>', f'<file>{input_file}</file>').replace('<file>$output</file>', f'<file>{output_file}</file>')

    with open(subset_orbit_temp, 'w') as file:
        file.write(updated_xml_content)

    print(f"Updated XML file saved to {subset_orbit_temp}")

    command1 = f"{gpt_path} {subset_orbit_temp} -q 16"
    now = dt.now()
    stat_print("process Sentinel 1 data")
    os.system(f"{command1} 2>&1 | grep -v '^WARNING:'")     # Suppress warnings
    print("Processing completed.")
    print("took ", dt.now() - now, " seconds")

    dim_to_tif = 'dim_to_tif.xml'
    dim_to_tif_temp = 'dim_to_tif_temp.xml'
    output_file_tif = output_file + '.tif'
    with open(dim_to_tif, 'r') as file:
        xml_content = file.read()
        updated_xml_content = xml_content.replace('<file>$input</file>', f'<file>{output_file}.dim</file>').replace('<file>$output</file>', f'<file>{output_file_tif}</file>')

    with open(dim_to_tif_temp, 'w') as file:
        file.write(updated_xml_content)

    print(f"Updated XML file saved to {dim_to_tif}")

    command2 = f"{gpt_path} {dim_to_tif_temp}"
    now = dt.now()
    stat_print("conversion to tif")
    os.system(f"{command2} 2>&1 | grep -v '^WARNING:'")
    print("Processing completed.")
    print("took ", dt.now() - now, " seconds")


merge_tif_files(input_folder)