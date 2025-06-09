#!/usr/bin/env python3
import json
import csv
import os
import sys
from collections import deque, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set
import uuid

# ——— CONFIG ———
INPUT_JSON = 'tbwa_drive_tree.json'
OUTPUT_CSV = 'dataset_campaign_assets.csv'
CHECKPOINT = '.build_checkpoint.json'
CHECKPOINT_INTERVAL = 500  # Save checkpoint every N rows
FOLDER_MIME = 'application/vnd.google-apps.folder'

# File type mappings
FILE_TYPES = {
    'application/vnd.google-apps.document': 'doc',
    'application/vnd.google-apps.spreadsheet': 'sheet',
    'application/vnd.google-apps.presentation': 'slides',
    'application/vnd.google-apps.folder': 'folder',
    'application/pdf': 'pdf',
    'image/jpeg': 'image',
    'image/png': 'image',
    'video/mp4': 'video',
    'video/quicktime': 'video',
    'application/zip': 'archive'
}

# Tenant mapping (you can extend this)
TENANT_MAPPING = {
    'default': 'scout',  # Default tenant for unmapped campaigns
    # Add campaign folder -> tenant mappings here
    # 'Campaign Name': 'tenant_id'
}

class DriveTreeProcessor:
    def __init__(self, input_json: str, output_csv: str):
        self.input_json = input_json
        self.output_csv = output_csv
        self.parent_map = defaultdict(list)  # child_id -> [parent_id,...]
        self.name_map = {}                   # id -> name
        self.mime_map = {}                   # id -> mimeType
        self.modified_map = {}               # id -> modifiedTime
        self.size_map = {}                   # id -> size
        self.campaign_folders: Dict[str, str] = {}  # id -> name
        self.tenant_map: Dict[str, str] = {}  # campaign -> tenant
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'skipped': 0,
            'errors': 0
        }

    def load_checkpoint(self) -> Dict:
        """Load checkpoint if it exists."""
        if os.path.exists(CHECKPOINT):
            with open(CHECKPOINT, 'r') as f:
                return json.load(f)
        return {"last_idx": -1, "timestamp": None}

    def save_checkpoint(self, idx: int):
        """Save current progress to checkpoint file."""
        state = {
            "last_idx": idx,
            "timestamp": datetime.utcnow().isoformat(),
            "stats": self.stats
        }
        with open(CHECKPOINT, 'w') as f:
            json.dump(state, f, indent=2)

    def load_data(self, resume: bool = False):
        """Load and process the Drive tree JSON."""
        print(f"📥 Loading Drive tree from {self.input_json}...")
        
        # Load checkpoint if resuming
        if resume:
            cp = self.load_checkpoint()
            start_idx = cp["last_idx"] + 1
            print(f"🔄 Resuming from index {start_idx}")
            if cp.get("timestamp"):
                print(f"   Last run: {cp['timestamp']}")
            if cp.get("stats"):
                self.stats = cp["stats"]
                print(f"   Previous stats: {self.stats}")
        else:
            start_idx = 0
        
        with open(self.input_json, 'r') as f:
            entries = json.load(f)

        # Build lookups
        for e in entries:
            file_id = e['id']
            self.name_map[file_id] = e['name']
            self.mime_map[file_id] = e['mimeType']
            self.modified_map[file_id] = e.get('modifiedTime', '')
            self.size_map[file_id] = e.get('size', 0)
            
            for p in e.get('parents', []):
                self.parent_map[file_id].append(p)

        # Find campaign folders
        self.campaign_folders = {
            fid: self.name_map[fid]
            for fid, mt in self.mime_map.items()
            if mt == FOLDER_MIME and 'root' in self.parent_map.get(fid, [])
        }

        # Build tenant mapping
        self.tenant_map = {
            name: TENANT_MAPPING.get(name, TENANT_MAPPING['default'])
            for name in self.campaign_folders.values()
        }

        self.stats['total_files'] = len(entries)
        print(f"✅ Loaded {len(entries)} files, found {len(self.campaign_folders)} campaign folders")

    def resolve_campaign(self, file_id: str) -> Optional[str]:
        """Walk up the tree to find the campaign folder."""
        visited: Set[str] = set()
        queue = deque(self.parent_map.get(file_id, []))
        
        while queue:
            pid = queue.popleft()
            if pid in self.campaign_folders:
                return self.campaign_folders[pid]
            if pid in visited:
                continue
            visited.add(pid)
            queue.extend(self.parent_map.get(pid, []))
        return None

    def get_file_type(self, mime_type: str) -> str:
        """Map MIME type to friendly file type."""
        return FILE_TYPES.get(mime_type, 'other')

    def write_dataset(self, resume: bool = False):
        """Write the processed dataset to CSV."""
        print(f"📝 Writing dataset to {self.output_csv}...")
        
        # Load checkpoint if resuming
        if resume:
            cp = self.load_checkpoint()
            start_idx = cp["last_idx"] + 1
        else:
            start_idx = 0
        
        # Open file in append mode if resuming
        mode = 'a' if resume else 'w'
        with open(self.output_csv, mode, newline='', encoding='utf-8') as out:
            writer = csv.writer(out)
            
            # Write header only for new files
            if not resume:
                writer.writerow([
                    'asset_id',
                    'file_id',
                    'file_name',
                    'file_type',
                    'mime_type',
                    'campaign_folder',
                    'tenant_id',
                    'size_bytes',
                    'modified_time',
                    'created_at'
                ])
            
            # Process files
            for idx, (fid, name) in enumerate(self.name_map.items()):
                # Skip up to start_idx when resuming
                if idx < start_idx:
                    continue
                
                try:
                    campaign = self.resolve_campaign(fid)
                    if not campaign:
                        self.stats['skipped'] += 1
                        continue
                    
                    writer.writerow([
                        str(uuid.uuid4()),  # Generate new asset_id
                        fid,
                        name,
                        self.get_file_type(self.mime_map[fid]),
                        self.mime_map[fid],
                        campaign,
                        self.tenant_map.get(campaign, TENANT_MAPPING['default']),
                        self.size_map.get(fid, 0),
                        self.modified_map.get(fid, ''),
                        datetime.utcnow().isoformat()
                    ])
                    
                    self.stats['processed'] += 1
                    
                    # Save checkpoint periodically
                    if (idx - start_idx + 1) % CHECKPOINT_INTERVAL == 0:
                        self.save_checkpoint(idx)
                        print(f"  • Checkpoint saved at index {idx}")
                        print(f"  • Progress: {self.stats['processed']}/{self.stats['total_files']} files")
                
                except Exception as e:
                    print(f"⚠️  Error processing file {fid}: {str(e)}")
                    self.stats['errors'] += 1
        
        # On clean completion, remove checkpoint
        if os.path.exists(CHECKPOINT):
            os.remove(CHECKPOINT)
            print("🧹 Checkpoint file removed — job complete")
        
        print("\n📊 Processing Summary:")
        print(f"- Total files: {self.stats['total_files']}")
        print(f"- Processed: {self.stats['processed']}")
        print(f"- Skipped: {self.stats['skipped']}")
        print(f"- Errors: {self.stats['errors']}")

def main():
    # Check for resume flag
    resume = '--resume' in sys.argv
    
    processor = DriveTreeProcessor(INPUT_JSON, OUTPUT_CSV)
    processor.load_data(resume)
    processor.write_dataset(resume)

if __name__ == "__main__":
    main() 