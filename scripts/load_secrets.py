#!/usr/bin/env python3
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import os
from pathlib import Path
from dotenv import load_dotenv

def load_secrets_from_keyvault():
    """Load secrets from Azure Key Vault and create .env file."""
    # Get Key Vault URL from environment or use default
    key_vault_url = os.getenv("AZURE_KEY_VAULT_URL")
    if not key_vault_url:
        print("❌ AZURE_KEY_VAULT_URL not set")
        return False

    try:
        # Authenticate to Azure
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_url, credential=credential)

        # List of secrets to fetch
        secrets = [
            "DATABASE_URL",
            "DRIVE_SERVICE_ACCOUNT_FILE",
            "DRIVE_CAMPAIGN_ROOT_ID",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "PINECONE_API_KEY",
            "PINECONE_ENV",
            "JWT_SECRET"
        ]

        # Create .env content
        env_content = []
        for secret_name in secrets:
            try:
                secret_value = client.get_secret(secret_name).value
                env_content.append(f"{secret_name}={secret_value}")
            except Exception as e:
                print(f"⚠️ Could not fetch {secret_name}: {str(e)}")

        # Write to .env file
        env_path = Path(".env")
        env_path.write_text("\n".join(env_content))
        print(f"✅ Secrets loaded to {env_path.absolute()}")
        return True

    except Exception as e:
        print(f"❌ Error loading secrets: {str(e)}")
        return False

if __name__ == "__main__":
    load_secrets_from_keyvault() 