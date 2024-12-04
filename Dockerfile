# Use a base image
FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-22.04

# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir -p /mnt/alinea_vol


# Update package list, upgrade packages, and install required packages
RUN apt-get update && \
    apt-get install -y \
    git \
    python3-pip \
    default-jre \
    gdal-bin \
    libgdal-dev \
    wget \
    expect && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install ipython requests pandas geopandas rasterio matplotlib tqdm gdal

#RUN git clone https://www.github.com/charlesmarseille/ALINEA /root/ALINEA



RUN chmod +x /root/ALINEA/scripts/download_and_install_snap.sh


# Run the script
RUN /root/ALINEA/scripts/download_and_install_snap.sh

#docker run -it --entrypoint "/bin/bash" -v ./data_example/:/mnt/alinea_vol test4

RUN cd /mnt/alinea_vol/

#run ["echo", "${zone}"]

CMD ["python3", "/ALINEA/scripts/download_sentinel1_from_extent.py"]

#data_example/fitri_extent.shp
