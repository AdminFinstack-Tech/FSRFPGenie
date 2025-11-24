#!/bin/bash

# Script to reprocess all failed documents
# Run this after deploying backend v15

API_URL="https://rfprag-backend.orangedesert-75e85877.eastus.azurecontainerapps.io/api"

# List of failed document IDs from user's JSON
FAILED_DOCS=(
  "69144fd724395ba32ce26ac4"
  "69144fe3cdc63f1c1b09e36c"
  "691450012b6bcd5e17bb8c17"
  "69166e0bac3f40f73e5aa5df"
  "691671d4a4fec618d68654ce"
  "69167320b07879bc5a2dd2c7"
  "691673c24e58b36c98c8e574"
  "6916746f4c13ed24b1368b35"
  "691675cc76c1c66d4e9f89d0"
  "6916762b88f33cf39b55cce7"
  "691676e58d05d82ec9e2e867"
  "6916cc294c9ab1af9c6a2db5"
  "6916cca87bb4e7fa6b4db9dd"
  "6871499543a35a2a41e8c1ec"
)

echo "====================================="
echo "Reprocessing Failed Documents"
echo "====================================="
echo ""
echo "API URL: $API_URL"
echo "Total documents to reprocess: ${#FAILED_DOCS[@]}"
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0

for doc_id in "${FAILED_DOCS[@]}"; do
  echo "Processing document: $doc_id"
  
  response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/documents/$doc_id/process" 2>&1)
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')
  
  if [ "$http_code" = "200" ]; then
    echo "  ✅ SUCCESS"
    ((SUCCESS_COUNT++))
  else
    echo "  ❌ FAILED (HTTP $http_code)"
    echo "  Response: $body"
    ((FAIL_COUNT++))
  fi
  
  echo ""
  sleep 2  # Delay between requests to avoid overload
done

echo "====================================="
echo "Reprocessing Complete"
echo "====================================="
echo "✅ Successful: $SUCCESS_COUNT"
echo "❌ Failed: $FAIL_COUNT"
echo ""

# Query documents status
echo "Checking updated document statuses..."
echo ""

curl -s "$API_URL/documents" | python3 -m json.tool | grep -A 2 "status"

echo ""
echo "====================================="
