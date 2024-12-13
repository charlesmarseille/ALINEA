$containers = docker ps -aq --filter ancestor=img_alinea

foreach ($containerId in $containers) {
    docker rm $containerId
}