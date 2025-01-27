$url = "https://github.com/charlesmarseille/ALINEA/archive/refs/heads/main.zip"
$destinationFolder = "C:\docker\"

if (!(Test-Path $destinationFolder)) {
    New-Item -ItemType Directory -Path $destinationFolder
}

try {
    Invoke-WebRequest -Uri $url -OutFile (Join-Path $destinationFolder "ALINEA.zip")
}
catch {
    Write-Error "Error downloading the file: $($_.Exception.Message)"
    exit
}

Expand-Archive -Path (Join-Path $destinationFolder "ALINEA.zip") -DestinationPath $destinationFolder

Remove-Item (Join-Path $destinationFolder "ALINEA.zip")

Rename-Item -Path (Join-Path $destinationFolder "ALINEA-main") -NewName (Join-Path $destinationFolder "ALINEA")

Invoke-Item (Join-Path $destinationFolder "ALINEA")

Write-Host "ALINEA downloaded, extracted, and moved successfully!"