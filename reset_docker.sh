#!/bin/sh

docker-compose down

# Removes existing containers
docker rm -f $(docker ps -a -q)

# Removes all volumes
docker volume rm $(docker volume ls -q)