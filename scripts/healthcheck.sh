#!/bin/sh
# Exit 0 if API is healthy, 1 otherwise (Docker / Coolify health probes).
set -eu
curl -sf --max-time 5 "http://localhost:8000/health" >/dev/null
