#!/usr/bin/env python3
from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from datetime import timedelta, datetime
import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional, Any
import subprocess
import uuid
from dataclasses import dataclass
from enum import Enum

# ——— CONFIG ———
RCLONE_CONFIG = os.getenv("RCLONE_CONFIG", "~/.config/rclone/rclone.conf")
DRIVE_REMOTE = os.getenv("DRIVE_REMOTE", "tbwa-drive")
ROOT_FOLDER = os.getenv("DRIVE_CAMPAIGN_ROOT_ID", "0AJMhu01UUQKoUk9PVA")
OUTPUT_DIR = Path("data")
CHECKPOINT_FILE = OUTPUT_DIR / ".drive_checkpoint.json"

class AssetType(Enum):
    FOLDER = "folder"
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    OTHER = "other"

@dataclass
class AssetMetadata:
    """Structured metadata for campaign assets."""
    asset_id: str
    file_name: str
    mime_type: str
    size_bytes: int
    modified_time: str
    created_time: str
    last_viewed_time: Optional[str]
    owner: Optional[str]
    folder_depth: int
    campaign_folder: str
    asset_type: AssetType
    listed_at: str
    uuid: str
    clean_path: str
    extension: str
    is_shared: bool
    shared_with: List[str]
    parent_folder: Optional[str]
    tags: List[str]

@task(
    retries=3,
    retry_delay_seconds=60,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1)
)
def list_drive_assets() -> List[Dict]:
    """List all assets in Drive folder with retries and caching."""
    logger = get_run_logger()
    logger.info("🔍 Listing Drive assets...")
    
    try:
        # Get detailed file listing with sharing info
        result = subprocess.run(
            [
                "rclone", "lsjson",
                f"{DRIVE_REMOTE}:{ROOT_FOLDER}",
                "--recursive",
                "--files-only",
                "--include", "*.{pdf,doc,docx,xls,xlsx,ppt,pptx,jpg,jpeg,png,mp4,mov}"
            ],
            check=True,
            capture_output=True,
            text=True
        )
        assets = json.loads(result.stdout)
        logger.info(f"✅ Found {len(assets)} assets")
        return assets
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ rclone failed: {e.stderr}")
        raise
    except json.JSONDecodeError:
        logger.error("❌ Failed to parse rclone output")
        raise

def _get_asset_type(mime_type: str, extension: str) -> AssetType:
    """Determine asset type from MIME type and extension."""
    if mime_type == "application/vnd.google-apps.folder":
        return AssetType.FOLDER
    
    if mime_type.startswith("image/"):
        return AssetType.IMAGE
    if mime_type.startswith("video/"):
        return AssetType.VIDEO
    if mime_type.startswith("audio/"):
        return AssetType.AUDIO
    
    doc_extensions = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}
    if extension.lower() in doc_extensions:
        return AssetType.DOCUMENT
    
    return AssetType.OTHER

@task
def process_assets(assets: List[Dict]) -> List[AssetMetadata]:
    """Process and enrich asset metadata."""
    logger = get_run_logger()
    logger.info("🔄 Processing assets...")
    
    processed = []
    for asset in assets:
        # Basic metadata
        path = asset.get("Path", "")
        name = asset.get("Name", "")
        extension = os.path.splitext(name)[1].lower()
        
        # Compute folder depth and parent
        parts = path.split("/")
        folder_depth = len(parts) - 1
        parent_folder = parts[-2] if folder_depth > 0 else None
        
        # Determine asset type
        asset_type = _get_asset_type(
            asset.get("MimeType", ""),
            extension
        )
        
        # Extract sharing info
        is_shared = asset.get("Shared", False)
        shared_with = asset.get("SharedWith", [])
        
        # Generate tags based on metadata
        tags = []
        if is_shared:
            tags.append("shared")
        if asset_type != AssetType.OTHER:
            tags.append(asset_type.value)
        if folder_depth > 2:
            tags.append("deep-nested")
        
        # Create structured metadata
        metadata = AssetMetadata(
            asset_id=asset["ID"],
            file_name=name,
            mime_type=asset.get("MimeType", ""),
            size_bytes=asset.get("Size", 0),
            modified_time=asset.get("ModTime", ""),
            created_time=asset.get("CreatedTime", ""),
            last_viewed_time=asset.get("LastViewed"),
            owner=asset.get("Owner"),
            folder_depth=folder_depth,
            campaign_folder=parts[0] if parts else "",
            asset_type=asset_type,
            listed_at=datetime.utcnow().isoformat(),
            uuid=str(uuid.uuid4()),
            clean_path=path.replace("\\", "/").strip("/"),
            extension=extension,
            is_shared=is_shared,
            shared_with=shared_with,
            parent_folder=parent_folder,
            tags=tags
        )
        
        processed.append(metadata)
    
    logger.info(f"✅ Processed {len(processed)} assets")
    return processed

@task
def write_checkpoint(assets: List[AssetMetadata]):
    """Write checkpoint for incremental runs."""
    logger = get_run_logger()
    logger.info("💾 Writing checkpoint...")
    
    checkpoint = {
        "timestamp": datetime.utcnow().isoformat(),
        "asset_count": len(assets),
        "asset_ids": [a.asset_id for a in assets],
        "metadata": {
            "total_size_bytes": sum(a.size_bytes for a in assets),
            "asset_types": {t.value: sum(1 for a in assets if a.asset_type == t) 
                          for t in AssetType},
            "shared_count": sum(1 for a in assets if a.is_shared),
            "max_depth": max(a.folder_depth for a in assets)
        }
    }
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=2)
    
    logger.info("✅ Checkpoint written")

@task
def write_csv(assets: List[AssetMetadata]):
    """Write assets to CSV for downstream processing."""
    logger = get_run_logger()
    logger.info("📝 Writing CSV...")
    
    csv_file = OUTPUT_DIR / "campaign_assets.csv"
    fieldnames = [
        "uuid", "asset_id", "file_name", "mime_type", "size_bytes",
        "modified_time", "created_time", "last_viewed_time", "owner",
        "folder_depth", "campaign_folder", "asset_type", "listed_at",
        "clean_path", "extension", "is_shared", "shared_with",
        "parent_folder", "tags"
    ]
    
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for asset in assets:
            row = {
                "uuid": asset.uuid,
                "asset_id": asset.asset_id,
                "file_name": asset.file_name,
                "mime_type": asset.mime_type,
                "size_bytes": asset.size_bytes,
                "modified_time": asset.modified_time,
                "created_time": asset.created_time,
                "last_viewed_time": asset.last_viewed_time,
                "owner": asset.owner,
                "folder_depth": asset.folder_depth,
                "campaign_folder": asset.campaign_folder,
                "asset_type": asset.asset_type.value,
                "listed_at": asset.listed_at,
                "clean_path": asset.clean_path,
                "extension": asset.extension,
                "is_shared": asset.is_shared,
                "shared_with": json.dumps(asset.shared_with),
                "parent_folder": asset.parent_folder,
                "tags": json.dumps(asset.tags)
            }
            writer.writerow(row)
    
    logger.info(f"✅ Wrote {len(assets)} rows to {csv_file}")

@task
def verify_output(assets: List[AssetMetadata]) -> bool:
    """Verify output files and counts."""
    logger = get_run_logger()
    logger.info("🔍 Verifying output...")
    
    # Check CSV exists and has right count
    csv_file = OUTPUT_DIR / "campaign_assets.csv"
    if not csv_file.exists():
        logger.error("❌ CSV file not found")
        return False
    
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if len(rows) != len(assets):
        logger.error(f"❌ CSV row count mismatch: {len(rows)} vs {len(assets)}")
        return False
    
    # Check checkpoint
    if not CHECKPOINT_FILE.exists():
        logger.error("❌ Checkpoint file not found")
        return False
    
    with open(CHECKPOINT_FILE, "r") as f:
        checkpoint = json.load(f)
    
    if checkpoint["asset_count"] != len(assets):
        logger.error(f"❌ Checkpoint count mismatch: {checkpoint['asset_count']} vs {len(assets)}")
        return False
    
    # Verify metadata consistency
    total_size = sum(a.size_bytes for a in assets)
    if checkpoint["metadata"]["total_size_bytes"] != total_size:
        logger.error("❌ Size metadata mismatch")
        return False
    
    logger.info("✅ Output verification passed")
    return True

@flow(name="Drive to Database Pipeline")
def build_campaign_dataset():
    """Main flow to build campaign dataset from Drive."""
    logger = get_run_logger()
    logger.info("🚀 Starting Drive to Database pipeline...")
    
    # List assets
    assets = list_drive_assets()
    
    # Process metadata
    processed = process_assets(assets)
    
    # Write outputs
    write_checkpoint(processed)
    write_csv(processed)
    
    # Verify
    if not verify_output(processed):
        raise Exception("Output verification failed")
    
    logger.info("✨ Pipeline completed successfully")

if __name__ == "__main__":
    build_campaign_dataset() 