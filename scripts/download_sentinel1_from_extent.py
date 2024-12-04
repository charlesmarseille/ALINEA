'''
Author: Charles Marseille, 2024
This script downloads Sentinel-1 data for specified zones and dates by performing the following steps:
1. Loads necessary libraries and sets up the environment.
2. Reads a shapefile containing the zones of interest.
3. Queries the Copernicus Open Access Hub for Sentinel-1 data within the specified date ranges.
4. Downloads the data for each zone and saves it to the local filesystem.

Usage:
    python download_sentinel1_from_extent.py <zone_name> <shapefile_path> <dates>

Example:
    python download_sentinel1_from_extent.py fitri zones/fitri_extent.shp 2024-01-09,2023-06-09,2023-01-09
'''


from datetime import date, timedelta, datetime as dt
import requests
import certifi
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
import os
from tqdm import tqdm
import urllib.parse
import sys

# if len(sys.argv) < -1: #4
#     print("Usage: python download_sentinel1_from_extent_test.py <zone_name> <shapefile_path> <dates>")
#     print("Example: python download_sentinel1_from_extent_test.py fitri zones/fitri_extent.shp 2024-01-09,2023-06-09,2023-01-09")
#     sys.exit(1)
# Load polygons from a shapefile
# zone_name = sys.argv[1]
# shapefile_path = sys.argv[2]
# dates = [dt.fromisoformat(date) for date in sys.argv[3].split(",")] 
zone_name = os.environ.get('zone')
shapefile_path = os.environ.get('shapefile_name')
dates = os.environ.get('capture_date')
|#dates = dates.toDate

# start_date = dt.today()
# dates = [(start_date - timedelta(days=90 * i)) for i in range(30)]

# # Copernicus credentials (change if needed)
copernicus_user = "cmarseille@cerfo.qc.ca"
copernicus_password = "passwordCerfo1234!"

# shapefile_path = f"zones/{zone_name}_extent.shp"
gdf = gpd.read_file(shapefile_path)


def get_keycloak(username: str, password: str) -> str:
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    try:
        r = requests.post(
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data=data,
        )
        r.raise_for_status()
    except Exception as e:
        raise Exception(
            f"Keycloak token creation failed. Response from the server was: {r.json()}"
        )
    return r.json()["access_token"]

# Function to query the Copernicus Open Access Hub
def query_copernicus(ft, start_date, end_date):
    url = (
        f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?"
        f"$filter=Collection/Name eq 'SENTINEL-1' and OData.CSC.Intersects(area=geography'SRID=4326;{ft}') "
        f"and ContentDate/Start gt {start_date}T00:00:00.000Z and ContentDate/End lt {end_date}T00:00:00.000Z"
        f"&$count=True&$top=1000"
    )
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def download_tile(product):
    try:
        save_path = f"data/{zone_name}/polygon{product['polygon_index']}/{product['feature']['Name']}.zip"
        # Ensure the directory exists
        download_dir = "data"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        if not os.path.exists(download_dir+"/"+zone_name):
            os.makedirs(download_dir+"/"+zone_name)
        if not os.path.exists(download_dir+"/"+zone_name+"/polygon"+str(product['polygon_index'])):
            os.makedirs(download_dir+"/"+zone_name+"/polygon"+str(product['polygon_index']))
        if os.path.exists(save_path):
            print(f"File {save_path} already exists. Skipping download.")

        print(f"Downloading {product['feature']['Name']} to {save_path}")
        start_time = dt.now()
        session = requests.Session()
        session.verify = certifi.where()  # Use certifi for SSL verification
        keycloak_token = get_keycloak(copernicus_user, copernicus_password)
        session.headers.update({"Authorization": f"Bearer {keycloak_token}"})
        url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({product['product_id']})/$value"        #(8b6b3639-4ca3-4eb5-ae01-ac89acf6ff50)

        # Stream the download and show progress bar
        with session.get(url, stream=True, verify=False, allow_redirects=True) as file:
            file.raise_for_status()
            total_size = int(file.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte
            t = tqdm(total=total_size, unit='iB', unit_scale=True)
            with open(save_path, "wb") as p:
                for data in file.iter_content(block_size):
                    t.update(len(data))
                    p.write(data)
            t.close()
        
        print(f"Downloaded {product['feature']['Name']} in {dt.now() - start_time}")
    except Exception as e:
        print(f"Problem with server: {e}")


def get_tiles(date, interval, day_offset):
    date_object = date
    time_interval = interval
    start_date = (date_object - timedelta(days=day_offset)).strftime("%Y-%m-%d")
    end_date = (date_object - timedelta(days=day_offset-interval)).strftime("%Y-%m-%d")
    # end_date = (date_object + timedelta(days=time_interval)).strftime("%Y-%m-%d")

    print('Get tiles for dates: ', start_date, end_date)
    # prods = [[] for _ in range(len(gdf))]
    # prods_count = 0
    # Iterate over each polygon in the shapefile
    for idx, row in gdf.iterrows():
        polygon = row.geometry
        polygon_index = idx
        ft = polygon.wkt  # WKT representation of the polygon

        # Query the Copernicus Open Access Hub
        json_ = query_copernicus(ft, start_date, end_date)
        
        p = pd.DataFrame.from_dict(json_["value"])  # Fetch available dataset
        if p.shape[0] > 0:
            p["geometry"] = p["GeoFootprint"].apply(shape)
            productDF = gpd.GeoDataFrame(p).set_geometry("geometry")  # Convert PD to GPD
            productDF = productDF[~productDF["Name"].str.contains("L1C")]  # Remove L1C dataset
            print(f"Total IW tiles found for polygon {idx}: {len(productDF)}")
            productDF["identifier"] = productDF["Name"].str.split(".").str[0]

            for _, feat in productDF.iterrows():
                product_info = {
                    "product_id": feat["Id"],
                    "polygon": polygon,
                    "polygon_index": polygon_index,
                    "capture_date": feat["ContentDate"]["Start"],
                    "feature": feat
                }
                # prods[i].append(product_info)
                products_info[i].append(product_info)
            # print("i, len prods: ", i, len(prods[i]))
            # prods_count += 1
        else:
            print(f"No data found for polygon {idx}")
            return False 

    # if prods_count == len(gdf):
    #     print(f"Found data for all polygons for interval {start_date} - {end_date}")
    #     for prod in prods:
    #         products_info.append(prod)
    return True

# Ensure data is found for each polygon
products_info = []
for i, date in enumerate(dates):
    j = 0
    interval = 15
    products_info.append([])
    while not get_tiles(date, interval, j):
        j += 1

for i,date in enumerate(dates):    # Print the collected product information
    for product in products_info[i]:
        print(f"Product ID: {product['product_id']}, Capture Date: {product['capture_date']}, Polygon index: {product['polygon_index']}")
        if ("IW_GRDH_1SDV" in product["feature"]["identifier"]) & ("COG" not in product["feature"]["identifier"]):
            download_tile(product)  
        else :
            print(f"Skipping { product['feature']['identifier'] }")

