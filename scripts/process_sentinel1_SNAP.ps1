param(
    [switch]$NoCache
)


try {

    if ($NoCache) {
        docker-compose -f c:/docker/ALINEA/docker-compose.yml --env-file ./config.env build --no-cache
    } else {
        docker-compose -f c:/docker/ALINEA/docker-compose.yml --env-file ./config.env build
    }
    docker-compose -f c:/docker/ALINEA/docker-compose.yml --env-file ./config.env run ALINEA bin/bash "/root/ALINEA/scripts/commands.sh"

    Read-Host "Commands done. Press enter to exit!"

} catch {
    Write-Warning "!!!An error occurred!!!: $($_.Exception.Message)"
    Read-Host "Press Enter to exit"
}