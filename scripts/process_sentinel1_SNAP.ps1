try {

    docker-compose -f c:/docker/ALINEA/docker-compose.yml -e ./config.env build

	docker-compose -f c:/docker/ALINEA/docker-compose.yml -e ./config.env run ALINEA bin/bash "/root/ALINEA/scripts/commands.sh"

	Read-Host "Commands done. Press enter to exit!"

} catch {
    Write-Warning "!!!An error occurred!!!: $($_.Exception.Message)"
    Read-Host "Press Enter to exit"
}

