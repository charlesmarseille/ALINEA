#Source the env file so the variables are accessible in the container

. /mnt/alinea_vol/config.env

cd /root/ALINEA
git pull

echo "----------------------------------------"
echo "--  Starting processing in container  --"
echo "----------------------------------------"
echo "cd to mnt/alinea_vol"
cd /mnt/alinea_vol/
echo "downloading data from sentinel1 for zone : ${ZONE}"
echo "Shapefile path: "$FOLDER_PATH"/"$SHAPEFILE_NAME
echo "Dates: ${CAPTURE_DATE}"
python3 /root/ALINEA/scripts/download_sentinel1_from_extent.py $ZONE "/mnt/alinea_vol/${SHAPEFILE_NAME}" $CAPTURE_DATE
python3 /root/alinea_vol/process_sentinel.py --input-folder "/mnt/alinea_vol/data/${ZONE}/polygon0" --shapefile "/mnt/alinea_vol/$SHAPEFILE_NAME"
echo "done."