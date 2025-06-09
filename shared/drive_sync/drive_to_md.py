#!/usr/bin/env python3
import os
import json
import argparse
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pypandoc

def get_drive_service():
    """Initialize and return Google Drive API service."""
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    return build('drive', 'v3', credentials=credentials)

def get_docs_service():
    """Initialize and return Google Docs API service."""
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        scopes=['https://www.googleapis.com/auth/documents.readonly']
    )
    return build('docs', 'v1', credentials=credentials)

def convert_doc_to_markdown(docs_service, file_id):
    """Convert a Google Doc to Markdown format."""
    doc = docs_service.documents().get(documentId=file_id).execute()
    html = doc.get('body', {}).get('content', [])
    # Convert HTML content to Markdown
    md = pypandoc.convert_text(html, 'gfm', format='html')
    return md

def process_doc(drive_service, docs_service, file_id, output_dir):
    """Process a single Google Doc and save as Markdown."""
    file = drive_service.files().get(fileId=file_id, fields='name,modifiedTime').execute()
    md_content = convert_doc_to_markdown(docs_service, file_id)
    
    # Create front matter
    front_matter = f"""---
title: {file['name']}
last_modified: {file['modifiedTime']}
drive_id: {file_id}
---

"""
    
    # Save to file
    output_path = os.path.join(output_dir, f"{file['name']}.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(front_matter + md_content)
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Sync Google Docs to Markdown files')
    parser.add_argument('--folder', required=True, help='Google Drive folder ID')
    parser.add_argument('--out', required=True, help='Output directory for Markdown files')
    parser.add_argument('--checkpoint', required=True, help='Checkpoint file path')
    args = parser.parse_args()

    # Initialize services
    drive_service = get_drive_service()
    docs_service = get_docs_service()

    # Get list of Google Docs in the folder
    results = drive_service.files().list(
        q=f"'{args.folder}' in parents and mimeType='application/vnd.google-apps.document'",
        fields="files(id, name, modifiedTime)"
    ).execute()
    
    # Process each document
    processed_files = []
    for file in results.get('files', []):
        output_path = process_doc(drive_service, docs_service, file['id'], args.out)
        processed_files.append({
            'id': file['id'],
            'name': file['name'],
            'path': output_path,
            'modified': file['modifiedTime']
        })

    # Save checkpoint
    with open(args.checkpoint, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'files': processed_files
        }, f, indent=2)

if __name__ == '__main__':
    main() 