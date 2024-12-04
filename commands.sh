#Source the env file so the variables are accessible in the container
. /mnt/alinea_vol/config.env

echo "!!!cd to mnt/alinea_vol"
cd /mnt/alinea_vol/

echo "downloading data from sentinel1 for zone : ${ZONE}"
echo "Shapefile path: '${FOLDERPATH}/${SHAPEFILE_NAME}'"
echo "Dates: ${CAPTURE_DATE}"
python3 /root/ALINEA/scripts/download_sentinel1_from_extent.py $ZONE "/mnt/alinea_vol/${SHAPEFILE_NAME}" $CAPTURE_DATE

echo "done."