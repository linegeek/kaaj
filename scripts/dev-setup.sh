#!/bin/bash
# First-time local dev setup.
# Run once after cloning the repo.
set -e

echo "==> Copying .env.example to .env"
cp -n .env.example .env || true

echo "==> Starting infrastructure (postgres, rabbitmq, hatchet)"
docker compose up -d postgres rabbitmq hatchet-migration hatchet-api hatchet-engine hatchet-setup-config

echo "==> Waiting for hatchet-setup-config to complete..."
docker compose wait hatchet-setup-config

echo "==> Retrieving Hatchet token"
bash scripts/get-hatchet-token.sh

echo ""
echo "Paste the token above into .env as HATCHET_CLIENT_TOKEN, then run:"
echo "  docker compose up backend worker frontend"
