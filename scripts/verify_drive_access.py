#!/usr/bin/env python3
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Dict, List, Optional
import sys

# ——— CONFIG ———
REQUIRED_ENV_VARS = [
    "DRIVE_SERVICE_ACCOUNT_FILE",
    "DRIVE_CAMPAIGN_ROOT_ID"
]

class DriveAccessVerifier:
    def __init__(self):
        self.creds = None
        self.service = None
        self.root_id = None

    def check_env(self) -> bool:
        """Verify all required environment variables are set."""
        missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
        if missing:
            print("❌ Missing required environment variables:")
            for var in missing:
                print(f"  - {var}")
            return False
        return True

    def verify_credentials(self) -> bool:
        """Verify service account credentials file exists and is valid."""
        creds_file = os.getenv("DRIVE_SERVICE_ACCOUNT_FILE")
        if not os.path.exists(creds_file):
            print(f"❌ Credentials file not found: {creds_file}")
            return False
        
        try:
            self.creds = service_account.Credentials.from_service_account_file(
                creds_file,
                scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"]
            )
            print("✅ Service account credentials loaded")
            return True
        except Exception as e:
            print(f"❌ Failed to load credentials: {str(e)}")
            return False

    def verify_drive_access(self) -> bool:
        """Verify we can access the Drive API and root folder."""
        try:
            self.service = build("drive", "v3", credentials=self.creds)
            self.root_id = os.getenv("DRIVE_CAMPAIGN_ROOT_ID")
            
            # Try to list files in root
            result = self.service.files().list(
                q=f"'{self.root_id}' in parents and trashed=false",
                pageSize=5,
                fields="files(id, name, mimeType)"
            ).execute()
            
            files = result.get("files", [])
            if not files:
                print("⚠️  No files found in root folder")
                return False
            
            print("\n📁 Sample files in root:")
            for f in files:
                print(f"  • {f['name']} ({f['mimeType']})")
            return True
            
        except HttpError as e:
            print(f"❌ Drive API error: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return False

    def verify_permissions(self) -> bool:
        """Verify we have the right permissions on the root folder."""
        try:
            # Try to get folder metadata
            folder = self.service.files().get(
                fileId=self.root_id,
                fields="id, name, capabilities"
            ).execute()
            
            caps = folder.get("capabilities", {})
            if not caps.get("canListChildren", False):
                print("❌ No permission to list folder contents")
                return False
            
            print(f"✅ Access verified for folder: {folder.get('name')}")
            return True
            
        except HttpError as e:
            print(f"❌ Permission error: {str(e)}")
            return False

    def run_checks(self) -> bool:
        """Run all verification checks."""
        print("🔍 Verifying Drive access setup...\n")
        
        checks = [
            ("Environment", self.check_env),
            ("Credentials", self.verify_credentials),
            ("Drive Access", self.verify_drive_access),
            ("Permissions", self.verify_permissions)
        ]
        
        all_passed = True
        for name, check in checks:
            print(f"\nChecking {name}...")
            if not check():
                all_passed = False
                print(f"❌ {name} check failed")
            else:
                print(f"✅ {name} check passed")
        
        if all_passed:
            print("\n✨ All checks passed! You're ready to use the Drive API.")
        else:
            print("\n⚠️  Some checks failed. Please fix the issues above.")
        
        return all_passed

def main():
    verifier = DriveAccessVerifier()
    success = verifier.run_checks()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 