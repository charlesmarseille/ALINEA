#Source the env file so the variables are accessible in the container

. /mnt/alinea_vol/config.env

cd /root/ALINEA
git stash
git pull

echo "----------------------------------------"
echo "--  Starting processing in container  --"
echo "----------------------------------------"
echo "cd to mnt/alinea_vol"
cd /mnt/alinea_vol/
echo "downloading data from sentinel1 for zone : ${ZONE}"
echo "Shapefile path: "$FOLDER_PATH"/"$SHAPEFILE_NAME
echo "Dates: ${CAPTURE_DATE}"

# Download data only if download is set to True
if [ "$DOWNLOAD" = "True" ]; then
  python3 /root/ALINEA/scripts/download_sentinel1_from_extent.py $ZONE "/mnt/alinea_vol/${SHAPEFILE_NAME}" $CAPTURE_DATE
fi

# Process data only if process is set to True (or download was successful)
if [ "$PROCESS" = "True" ]; then
  python3 /root/ALINEA/scripts/process_sentinel.py --input-folder "/mnt/alinea_vol/data/${ZONE}/polygon0" --zone $ZONE --shapefile "/mnt/alinea_vol/$SHAPEFILE_NAME"
fi

echo "done."