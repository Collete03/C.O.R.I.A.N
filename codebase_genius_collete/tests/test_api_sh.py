#!/bin/bash

echo "🧪 Testing Codebase Genius API"
echo "================================"

# Test JSON request
echo ""
echo "1. Testing JSON request..."
curl -X POST "http://127.0.0.1:8000/generate" \
-H "Content-Type: application/json" \
-d '{"github_url": "https://github.com/Collete03/C.O.R.I.A.N", "use_llm": true}' \
-w "\n⏱ Status: %{http_code}\n"

echo ""
echo "2. Testing form data request..."
# Test form data request  
curl -X POST "http://127.0.0.1:8000/generate" \
-F "github_url=https://github.com/Collete03/C.O.R.I.A.N" \
-F "use_llm=true" \
-w "\n⏱ Status: %{http_code}\n"

echo ""
echo "3. Testing health endpoint..."
curl -s "http://127.0.0.1:8000/health" | jq .

echo ""
echo "✅ All tests completed!"