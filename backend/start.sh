set -e

docker ps --filter "publish=27017" --format "{{.ID}} {{.Names}}" | awk '$2 != "passa_o_bastao_mongodb" {print $1}' | xargs -r docker stop
docker ps --filter "publish=8000" --format "{{.ID}} {{.Names}}" | awk '$2 != "passa_o_bastao_backend" {print $1}' | xargs -r docker stop

docker compose up --build --force-recreate -d
