param(
  [switch]$NoCache
)

# Create a timestamp for the log file name
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$logFile = "docker_build_$(if ($NoCache) {"no_cache_"}).log"  # Log file with timestamp and NoCache indicator

# Execute the commands and redirect output and error to the log file
try {
  if ($NoCache) {
    docker-compose -f c:/docker/ALINEA/docker-compose.yml --env-file ./config.env build --no-cache 2>&1 | Tee-Object -FilePath $logFile -Append
  } else {
    docker-compose -f c:/docker/ALINEA/docker-compose.yml --env-file ./config.env build 2>&1 | Tee-Object -FilePath $logFile -Append
  }

  docker-compose -f c:/docker/ALINEA/docker-compose.yml --env-file ./config.env run ALINEA bin/bash "/root/ALINEA/scripts/commands.sh" 2>&1 | Tee-Object -FilePath $logFile -Append

  Write-Host "Commands done. Press enter to exit!"
} catch {
  Write-Error "!!!An error occurred!!!: $($_.Exception.Message)" | Out-File -FilePath $logFile -Append -Encoding UTF8
  Read-Host "Press Enter to exit"
}