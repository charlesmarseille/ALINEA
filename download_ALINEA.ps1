$url = "https://github.com/charlesmarseille/ALINEA/archive/refs/heads/main.zip"
$destinationFolder = "C:\docker\ALINEA"

# Create the destination folder if it doesn't exist
if (!(Test-Path $destinationFolder)) {
    New-Item -ItemType Directory -Path $destinationFolder
}

# Download the zip file
try {
    Invoke-WebRequest -Uri $url -OutFile (Join-Path $destinationFolder "ALINEA.zip")
}
catch {
    Write-Error "Error downloading the file: $($_.Exception.Message)"
    exit
}

# Extract the zip file
Expand-Archive -Path (Join-Path $destinationFolder "ALINEA.zip") -DestinationPath $destinationFolder

# Remove the downloaded zip file (optional)
Remove-Item (Join-Path $destinationFolder "ALINEA.zip")

# Find the ALINEA-main folder (it's the only subfolder after extraction)
$extractedFolder = Get-ChildItem -Path $destinationFolder | Where-Object {$_.PSIsContainer}

if ($extractedFolder) {
    # Copy the contents of ALINEA-main to the parent directory (C:\docker)
    Copy-Item -Path (Join-Path $extractedFolder.FullName "*") -Destination $destinationFolder -Force -Recurse

    # Remove the ALINEA-main folder
    Remove-Item -Path $extractedFolder.FullName -Force -Recurse

    # Open the destination folder in Explorer
    Invoke-Item $destinationFolder
}
else {
    Write-Warning "Could not find the extracted ALINEA-main folder."
}

Write-Host "ALINEA downloaded, extracted, and moved successfully!"