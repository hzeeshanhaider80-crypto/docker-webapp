#!/usr/bin/env bash
# Deploy a specific image version and check it's healthy.
# Usage: bash scripts/deploy.sh ghcr.io/<user>/docker-webapp:<tag>
# Rollback = run it with an older tag.

# Stop on any error (-e), on undefined variables (-u) and on failures inside pipes.
set -euo pipefail

# First argument = the full image name. ':?' stops with this message if it's missing.
IMAGE="${1:?Usage: bash scripts/deploy.sh <image>   e.g. ghcr.io/user/docker-webapp:abc1234}"

# Always work from the project folder (the folder above scripts/).
cd "$(dirname "$0")/.."

# docker-compose.yml reads WEB_IMAGE to know which image to run.
export WEB_IMAGE="$IMAGE"

echo "==> 1/4 Deploying image: $WEB_IMAGE"

echo "==> 2/4 Pulling images"
# Download the new app image (and redis/nginx updates if any).
docker compose pull --quiet

echo "==> 3/4 Starting containers"
# -d = background. Only containers whose image changed are recreated.
# --no-build = never build on the server; always use the image from GHCR.
docker compose up -d --no-build --remove-orphans

echo "==> 4/4 Waiting for the app to be healthy"
# Ask /health through Nginx up to 30 times, 2 seconds apart (about 1 minute).
for i in $(seq 1 30); do
  if curl -sf http://localhost/health > /dev/null; then
    echo "✅ Healthy after $i attempt(s)"
    # Delete old, unused images to free disk space.
    docker image prune -f > /dev/null
    echo "🚀 Deployment complete: $WEB_IMAGE"
    exit 0
  fi
  sleep 2
done

# Never became healthy: show logs and exit with an error, so GitHub marks the deploy as failed.
echo "❌ App did not become healthy. Recent logs:"
docker compose logs --tail=40 web
exit 1
