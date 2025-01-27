import geopandas as gpd
from shapely.geometry import Polygon

def get_overall_bounding_box_latlon(input_shapefile, output_shapefile):
    """Calculates a single bounding box encompassing all features in a shapefile and saves it as a new shapefile in lat/lon (WGS 84).

    Args:
        input_shapefile (str): Path to the input shapefile.
        output_shapefile (str): Path to save the output bounding box shapefile.
    """
    try:
        gdf = gpd.read_file(input_shapefile)
        if gdf.empty:
            raise ValueError("Input shapefile is empty.")

        # Project to WGS 84 (EPSG:4326) if it's not already
        if gdf.crs is None or gdf.crs != "epsg:4326":
            gdf = gdf.to_crs("epsg:4326")

        minx = gdf.bounds['minx'].min()
        miny = gdf.bounds['miny'].min()
        maxx = gdf.bounds['maxx'].max()
        maxy = gdf.bounds['maxy'].max()

        bbox = Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)])
        bbox_gdf = gpd.GeoDataFrame({'geometry': [bbox]}, crs="epsg:4326")  # Explicitly set CRS

        bbox_gdf.to_file(output_shapefile)
        print(f"Overall bounding box saved to: {output_shapefile} in WGS 84 (lat/lon).")

    except FileNotFoundError:
        print(f"Error: Input shapefile not found.")
    except ValueError as e:
        print(f"ValueError: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
input_shp = "path/to/your/input.shp"  # Replace with the path to your input shapefile
output_shp = "path/to/your/output_overall_bbox_latlon.shp" # Replace with the desired output path
get_overall_bounding_box_latlon(input_shp, output_shp)