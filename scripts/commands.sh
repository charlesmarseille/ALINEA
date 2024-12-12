echo "cd to mnt/alinea_vol"
cd /mnt/alinea_vol/

echo "downloading data from sentinel1 for zone : $ZONE"
echo "Shapefile path: '${FOLDERPATH}/${SHAPEFILE_NAME}'"
echo "Dates: $CAPTURE_DATE"
python3 /root/ALINEA/scripts/download_sentinel1_from_extent.py $ZONE "${FOLDERPATH}/${SHAPEFILE_NAME}" $CAPTURE_DATE

echo "done."