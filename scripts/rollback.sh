#!/usr/bin/env bash
# Manual rollback - run on the VM as: ./scripts/rollback.sh
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -f .last_good_tag ]]; then
  echo "No .last_good_tag recorded. Inspect available image tags and set IMAGE_TAG in .env."
  exit 1
fi

previous_tag=$(tr -d '[:space:]' < .last_good_tag)
if [[ -z "$previous_tag" ]]; then
  echo ".last_good_tag is empty; refusing to change the deployment."
  exit 1
fi

echo "Rolling back to image tag: $previous_tag"
if grep -q '^IMAGE_TAG=' .env; then
  sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=$previous_tag/" .env
else
  printf '\nIMAGE_TAG=%s\n' "$previous_tag" >> .env
fi

docker compose pull app app-2 greeting-service
docker compose up -d --no-deps app app-2 greeting-service

for attempt in $(seq 1 10); do
  if curl -fsS http://localhost/readyz >/dev/null; then
    echo "Rollback verified."
    exit 0
  fi
  echo "Readiness attempt $attempt failed; retrying..."
  sleep 3
done

echo "Rollback image started but did not become ready."
exit 1
