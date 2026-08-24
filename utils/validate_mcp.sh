#!/usr/bin/env bash
set -euo pipefail

# Validate environment variables
: "${AAP_HOST:?Environment variable AAP_HOST is required}"
: "${AAP_MCP_PORT:?Environment variable AAP_MCP_PORT is required}"
: "${AAP_TOKEN:?Environment variable AAP_TOKEN is required}"

BASE_URL="https://${AAP_HOST}:${AAP_MCP_PORT}"

# 1. Health check
echo "Checking API health..."
curl -s -f -H "Authorization: Bearer ${AAP_TOKEN}" "${BASE_URL}/api/v1/health"
echo -e "\n"

# 2. Initialize MCP session and dump headers to capture session ID
echo "Initializing MCP Session..."
RESPONSE_HEADERS=$(curl -s -D - -o /dev/null -X POST \
  -H "Authorization: Bearer ${AAP_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "curl-client",
        "version": "1.0.0"
      }
    },
    "id": 1
  }' \
  "${BASE_URL}/mcp/")

# Extract mcp-session-id
MCP_SESSION_ID=$(echo "${RESPONSE_HEADERS}" | grep -i '^mcp-session-id:' | awk '{print $2}' | tr -d '\r')

if [[ -z "${MCP_SESSION_ID}" ]]; then
  echo "Error: Failed to extract 'mcp-session-id' from initialization headers." >&2
  exit 1
fi

echo "Captured Session ID: ${MCP_SESSION_ID}"
echo "----------------------------------------"

# 3. Fetch tools list, strip SSE prefix, delete inputSchema, and truncate array
echo "Fetching tools list..."
curl -s -X POST \
  -H "Authorization: Bearer ${AAP_TOKEN}" \
  -H "Mcp-Session-Id: ${MCP_SESSION_ID}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 2
  }' \
  "${BASE_URL}/mcp/" \
  | sed -n 's/^data: //p' \
  | jq '.result.tools |= [(.[0] | del(.inputSchema)), "..."]'
