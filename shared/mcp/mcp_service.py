from typing import Dict, Optional
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import pinecone

class MCPService:
    def __init__(self):
        # Initialize Azure
        self.azure_credential = DefaultAzureCredential()
        self.keyvault_client = SecretClient(
            vault_url=f"https://kv-tbwa-juicer-insights2.vault.azure.net/",
            credential=self.azure_credential
        )

        # Initialize Google Drive
        self.drive_creds = service_account.Credentials.from_service_account_file(
            os.getenv('DRIVE_SERVICE_ACCOUNT_FILE'),
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.drive_service = build('drive', 'v3', credentials=self.drive_creds)

        # Initialize Pinecone
        pinecone.init(
            api_key=os.getenv('PINECONE_API_KEY'),
            environment=os.getenv('PINECONE_ENV')
        )

    def get_azure_secret(self, secret_name: str) -> str:
        """Get a secret from Azure Key Vault."""
        return self.keyvault_client.get_secret(secret_name).value

    def list_drive_files(self, folder_id: str) -> list:
        """List files in a Google Drive folder."""
        results = self.drive_service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name, mimeType)"
        ).execute()
        return results.get('files', [])

    def store_vector(self, index_name: str, vectors: list, metadata: Optional[Dict] = None):
        """Store vectors in Pinecone."""
        index = pinecone.Index(index_name)
        index.upsert(vectors=vectors, metadata=metadata)

    def query_vector(self, index_name: str, vector: list, top_k: int = 5) -> list:
        """Query vectors from Pinecone."""
        index = pinecone.Index(index_name)
        return index.query(vector=vector, top_k=top_k)

    def sync_across_clouds(self, source: str, destination: str, data: Dict):
        """Sync data across different cloud providers."""
        if source == 'drive' and destination == 'pinecone':
            # Example: Sync Drive document embeddings to Pinecone
            vectors = self._extract_vectors_from_drive(data['file_id'])
            self.store_vector('document-embeddings', vectors, metadata=data)
        elif source == 'pinecone' and destination == 'drive':
            # Example: Sync Pinecone results back to Drive
            self._create_drive_summary(data['query_results']) 