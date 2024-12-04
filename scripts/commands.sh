echo "cd to mnt/alinea_vol"
cd /mnt/alinea_vol/

echo "downloading data from sentinel1..."
python3 /root/ALINEA/scripts/download_sentinel1_from_extent.py $ZONE $SHAPEFILE_PATH $CAPTURE_DATE

echo "done."