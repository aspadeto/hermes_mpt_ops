docker compose down
docker volume rm as7_hermes-agent-src
docker compose pull
docker compose up -d
