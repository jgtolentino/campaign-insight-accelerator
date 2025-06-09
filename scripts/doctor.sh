#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo -e "\n🩺  Running full-stack health check...\n"

# 0. Load secrets from Azure Key Vault
echo "0️⃣  Loading secrets from Azure Key Vault..."
if ! az account show &> /dev/null; then
  echo "❌ Not logged in to Azure. Please run 'az login' first."
  exit 1
fi

# Function to fetch secret with error handling
fetch_secret() {
    local secret_name=$1
    local env_var=$2
    local value
    
    echo "Fetching $secret_name..."
    value=$(az keyvault secret show --vault-name kv-tbwa-juicer-insights2 --name "$secret_name" --query value -o tsv 2>/dev/null)
    
    if [ $? -eq 0 ] && [ ! -z "$value" ]; then
        export "$env_var=$value"
        echo "✅ $secret_name loaded successfully"
    else
        echo "⚠️ Could not fetch $secret_name: $value"
    fi
}

# Fetch secrets with correct names
fetch_secret "OPENAI-API-KEY" "AZURE_OPENAI_API_KEY"
fetch_secret "DATABASE-URL" "DATABASE_URL"
fetch_secret "DRIVE-SERVICE-ACCOUNT-FILE" "DRIVE_SERVICE_ACCOUNT_FILE"
fetch_secret "DRIVE-CAMPAIGN-ROOT-ID" "DRIVE_CAMPAIGN_ROOT_ID"
fetch_secret "AZURE-OPENAI-ENDPOINT" "AZURE_OPENAI_ENDPOINT"
fetch_secret "PINECONE-API-KEY" "PINECONE_API_KEY"
fetch_secret "PINECONE-ENV" "PINECONE_ENV"
fetch_secret "JWT-SECRET" "JWT_SECRET"

# 1. ENV VARS
echo -e "\n1️⃣  Checking required environment variables..."
required_env=(DATABASE_URL \
              AZURE_OPENAI_API_KEY AZURE_OPENAI_ENDPOINT \
              DRIVE_SERVICE_ACCOUNT_FILE DRIVE_CAMPAIGN_ROOT_ID \
              PINECONE_API_KEY PINECONE_ENV \
              JWT_SECRET)
missing_env=()
for v in "${required_env[@]}"; do
  if [[ -z "${!v-}" ]]; then
    missing_env+=("$v")
  fi
done
if (( ${#missing_env[@]} )); then
  echo "❌ Missing env vars: ${missing_env[*]}"
  echo "   → please add to your .env or export them and re-run."
  exit 1
else
  echo "✅ All env vars set."
fi

# 2. PYTHONPATH sanity
echo -e "\n2️⃣  Verifying PYTHONPATH includes project root..."
if ! python3 -c "import sys, os; assert os.getcwd() in sys.path" &>/dev/null; then
  echo "  • Injecting project root into PYTHONPATH for this run..."
  export PYTHONPATH="$REPO_ROOT:${PYTHONPATH:-}"
else
  echo "✅ PYTHONPATH OK."
fi

# 3. PostgreSQL readiness
echo -e "\n3️⃣  Testing DB connection..."
if ! pg_isready -q; then
  echo "❌ PostgreSQL not ready on default host/port."
  exit 1
fi

if ! psql "$DATABASE_URL" -c '\q' &>/dev/null; then
  echo "❌ Cannot connect to DB with \$DATABASE_URL."
  exit 1
else
  echo "✅ DB connection successful."
fi

# 4. Alembic migrations health
echo -e "\n4️⃣  Checking Alembic heads & duplicate columns…"
heads=($(alembic heads --verbose | grep 'head:' | awk '{print $2}'))
if (( ${#heads[@]} > 1 )); then
  echo "⚠️  Multiple Alembic heads detected: ${heads[*]}"
  echo "   To merge, run:"
  echo "     alembic merge -m \"Merge heads\" ${heads[*]}"
else
  echo "✅ Single Alembic head: ${heads[0]:-none}"
fi

echo -n "→ Scanning for duplicate tenant_id or tag_id adds… "
dups=$(grep -R "add_column.*tenant_id" alembic/versions || true)
if [[ -n "$dups" ]]; then
  echo "⚠️  Found multiple migrations adding tenant_id:"
  echo "$dups" | sed 's/^/   • /'
  echo "   → Please remove duplicates so each table's tenant_id is only added once."
else
  echo "✅ No duplicate tenant_id additions found."
fi

echo -n "→ Scanning for tag tables migration… "
if ! grep -R "create_table('tags'" alembic/versions &>/dev/null; then
  echo "❌ No metadata-tagging revision found."
  echo "   → Add tags/campaign_tags/asset_tags via the 20250608_add_metadata_tagging.py script."
else
  echo "✅ Metadata-tagging migrations present."
fi

# 5. Attempt a dry-run migrate
echo -e "\n5️⃣  Attempting Alembic upgrade --sql (dry-run)…"
if ! alembic upgrade --sql head &>/dev/null; then
  echo "❌ Alembic dry-run failed. Inspect the SQL above for error clues."
else
  echo "✅ Alembic dry-run OK."
fi

# 6. Google Drive credentials check
echo -e "\n6️⃣  Verifying Google Drive creds & access…"
python3 - <<'PYCODE'
import os, json, sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds_file = os.getenv("DRIVE_SERVICE_ACCOUNT_FILE", "")
if not os.path.isfile(creds_file):
    print("❌ DRIVE_SERVICE_ACCOUNT_FILE not found at", creds_file)
    sys.exit(1)
creds = service_account.Credentials.from_service_account_file(
    creds_file,
    scopes=['https://www.googleapis.com/auth/drive.metadata.readonly']
)
service = build('drive', 'v3', credentials=creds)
root_id = os.getenv("DRIVE_CAMPAIGN_ROOT_ID", "")
res = service.files().list(q=f"'{root_id}' in parents and trashed=false", pageSize=5).execute()
if 'files' not in res:
    print("❌ Unable to list files under root:", root_id)
    sys.exit(1)
print("✅ Google Drive access OK. Sample files:")
for f in res['files']:
    print("   •", f['name'], "(", f['mimeType'], ")")
PYCODE

# 7. Final summary
echo -e "\n🎉  All checks passed—or actionable items flagged above. You're ready to proceed!" 