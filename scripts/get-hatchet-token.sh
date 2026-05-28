#!/bin/bash
# Reads the Hatchet API token written by hatchet-setup-config.
# Run after: docker compose up hatchet-setup-config
#
# Usage: ./scripts/get-hatchet-token.sh
#   Then paste the token into your .env as HATCHET_CLIENT_TOKEN=...

TOKEN_FILE="$(docker volume inspect kaaj_hatchet_config --format '{{ .Mountpoint }}')/token"

if [ ! -f "$TOKEN_FILE" ]; then
  echo "Token file not found. Make sure hatchet-setup-config has completed:"
  echo "  docker compose up hatchet-setup-config"
  exit 1
fi

TOKEN=$(cat "$TOKEN_FILE")
echo ""
echo "Hatchet client token:"
echo "$TOKEN"
echo ""
echo "Add this to your .env file:"
echo "HATCHET_CLIENT_TOKEN=$TOKEN"
