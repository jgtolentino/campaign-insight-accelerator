#!/usr/bin/env python3
import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

# ——— CONFIG ———
RCLONE_CONFIG = os.getenv("RCLONE_CONFIG", "~/.config/rclone/rclone.conf")
DRIVE_REMOTE = os.getenv("DRIVE_REMOTE", "tbwa-drive")
ROOT_FOLDER = os.getenv("DRIVE_CAMPAIGN_ROOT_ID", "0AJMhu01UUQKoUk9PVA")
LOG_DIR = Path("logs")
CHECKPOINT_FILE = ".drive_monitor_checkpoint.json"

# ——— LOGGING ———
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "drive_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DriveStats:
    total_files: int = 0
    total_size: int = 0
    modified_last_24h: int = 0
    shared_files: int = 0
    error_count: int = 0

class DriveMonitor:
    def __init__(self):
        self.stats = DriveStats()
        self.checkpoint = self._load_checkpoint()
        
        # Ensure log directory exists
        LOG_DIR.mkdir(exist_ok=True)
        
        # Verify rclone is installed
        try:
            subprocess.run(["rclone", "version"], check=True, capture_output=True)
            logger.info("✅ rclone is installed")
        except subprocess.CalledProcessError:
            logger.error("❌ rclone is not installed or not in PATH")
            raise

    def _load_checkpoint(self) -> Dict:
        """Load last checkpoint if it exists."""
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, 'r') as f:
                return json.load(f)
        return {"last_run": None, "processed_files": set()}

    def _save_checkpoint(self):
        """Save current checkpoint."""
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump({
                "last_run": datetime.utcnow().isoformat(),
                "processed_files": list(self.checkpoint["processed_files"])
            }, f)

    def _run_rclone(self, cmd: List[str]) -> Dict:
        """Run rclone command and parse JSON output."""
        try:
            result = subprocess.run(
                ["rclone"] + cmd,
                check=True,
                capture_output=True,
                text=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ rclone command failed: {e.stderr}")
            self.stats.error_count += 1
            return {}
        except json.JSONDecodeError:
            logger.error("❌ Failed to parse rclone output as JSON")
            self.stats.error_count += 1
            return {}

    def check_folder_structure(self) -> bool:
        """Verify folder structure and permissions."""
        logger.info("🔍 Checking folder structure...")
        
        # List root folder
        result = self._run_rclone([
            "lsjson",
            f"{DRIVE_REMOTE}:{ROOT_FOLDER}",
            "--recursive",
            "--files-only"
        ])
        
        if not result:
            return False
        
        # Update stats
        self.stats.total_files = len(result)
        self.stats.total_size = sum(f.get("Size", 0) for f in result)
        
        # Check for recently modified files
        cutoff = datetime.utcnow().timestamp() - 86400  # 24 hours
        self.stats.modified_last_24h = sum(
            1 for f in result 
            if f.get("ModTime", 0) > cutoff
        )
        
        logger.info(f"📊 Found {self.stats.total_files} files")
        logger.info(f"📊 Total size: {self.stats.total_size / 1024 / 1024:.1f} MB")
        logger.info(f"📊 Modified in last 24h: {self.stats.modified_last_24h}")
        return True

    def check_permissions(self) -> bool:
        """Check file sharing and permissions."""
        logger.info("🔒 Checking permissions...")
        
        # Get sharing info
        result = self._run_rclone([
            "lsjson",
            f"{DRIVE_REMOTE}:{ROOT_FOLDER}",
            "--recursive",
            "--files-only",
            "--include", "*.{pdf,doc,docx,xls,xlsx,ppt,pptx}"
        ])
        
        if not result:
            return False
        
        # Count shared files
        self.stats.shared_files = sum(
            1 for f in result 
            if f.get("Shared", False)
        )
        
        logger.info(f"📊 Shared files: {self.stats.shared_files}")
        return True

    def verify_checksums(self) -> bool:
        """Verify file integrity with checksums."""
        logger.info("🔍 Verifying file integrity...")
        
        result = self._run_rclone([
            "check",
            f"{DRIVE_REMOTE}:{ROOT_FOLDER}",
            "--one-way",
            "--checksum"
        ])
        
        if not result:
            return False
        
        logger.info("✅ Checksum verification complete")
        return True

    def generate_report(self) -> Dict:
        """Generate monitoring report."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "stats": {
                "total_files": self.stats.total_files,
                "total_size_mb": self.stats.total_size / 1024 / 1024,
                "modified_last_24h": self.stats.modified_last_24h,
                "shared_files": self.stats.shared_files,
                "error_count": self.stats.error_count
            },
            "checkpoint": {
                "last_run": self.checkpoint["last_run"],
                "processed_files": len(self.checkpoint["processed_files"])
            }
        }

    def run_checks(self) -> bool:
        """Run all monitoring checks."""
        logger.info("🚀 Starting Drive monitoring checks...")
        
        checks = [
            ("Folder Structure", self.check_folder_structure),
            ("Permissions", self.check_permissions),
            ("Checksums", self.verify_checksums)
        ]
        
        all_passed = True
        for name, check in checks:
            logger.info(f"\nRunning {name} check...")
            if not check():
                all_passed = False
                logger.error(f"❌ {name} check failed")
            else:
                logger.info(f"✅ {name} check passed")
        
        # Save checkpoint
        self._save_checkpoint()
        
        # Generate report
        report = self.generate_report()
        logger.info("\n📊 Monitoring Report:")
        logger.info(json.dumps(report, indent=2))
        
        return all_passed

def main():
    monitor = DriveMonitor()
    success = monitor.run_checks()
    exit(0 if success else 1)

if __name__ == "__main__":
    main() 