#!/usr/bin/env python3
import os
import sys
import csv
from datetime import datetime
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ——— CONFIG ———
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/cesdb")
INPUT_CSV = "dataset_campaign_assets.csv"
BATCH_SIZE = 1000  # Number of rows to insert at once

# SQL for table creation
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS campaign_assets (
    asset_id UUID PRIMARY KEY,
    file_id TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    campaign_folder TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    size_bytes BIGINT,
    modified_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE(file_id, tenant_id)
);

CREATE INDEX IF NOT EXISTS idx_campaign_assets_tenant_id 
    ON campaign_assets(tenant_id);
CREATE INDEX IF NOT EXISTS idx_campaign_assets_campaign_folder 
    ON campaign_assets(campaign_folder);
CREATE INDEX IF NOT EXISTS idx_campaign_assets_file_type 
    ON campaign_assets(file_type);
"""

# SQL for upsert
UPSERT_SQL = """
INSERT INTO campaign_assets (
    asset_id, file_id, file_name, file_type, mime_type,
    campaign_folder, tenant_id, size_bytes, modified_time,
    created_at, updated_at
) VALUES %s
ON CONFLICT (asset_id) DO UPDATE SET
    file_name = EXCLUDED.file_name,
    file_type = EXCLUDED.file_type,
    mime_type = EXCLUDED.mime_type,
    campaign_folder = EXCLUDED.campaign_folder,
    tenant_id = EXCLUDED.tenant_id,
    size_bytes = EXCLUDED.size_bytes,
    modified_time = EXCLUDED.modified_time,
    updated_at = EXCLUDED.updated_at;
"""

class DatasetLoader:
    def __init__(self, db_url: str, input_csv: str):
        self.db_url = db_url
        self.input_csv = input_csv
        self.conn = None
        self.cursor = None
        self.stats = {
            'total_rows': 0,
            'inserted': 0,
            'updated': 0,
            'errors': 0
        }

    def connect(self):
        """Establish database connection."""
        print("🔌 Connecting to database...")
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.conn.cursor()
            print("✅ Connected successfully")
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            raise

    def create_table(self):
        """Create the campaign_assets table if it doesn't exist."""
        print("📝 Creating table if not exists...")
        try:
            self.cursor.execute(CREATE_TABLE_SQL)
            print("✅ Table created/verified")
        except Exception as e:
            print(f"❌ Table creation failed: {str(e)}")
            raise

    def validate_row(self, row: Dict) -> bool:
        """Validate a row of data."""
        required_fields = ['asset_id', 'file_id', 'file_name', 'file_type', 
                         'mime_type', 'campaign_folder', 'tenant_id']
        
        # Check required fields
        for field in required_fields:
            if not row.get(field):
                print(f"⚠️  Missing required field '{field}' in row: {row}")
                return False
        
        # Validate UUID
        try:
            uuid.UUID(row['asset_id'])
        except ValueError:
            print(f"⚠️  Invalid UUID '{row['asset_id']}' in row: {row}")
            return False
        
        # Validate timestamps
        try:
            if row.get('modified_time'):
                datetime.fromisoformat(row['modified_time'].replace('Z', '+00:00'))
        except ValueError:
            print(f"⚠️  Invalid modified_time '{row['modified_time']}' in row: {row}")
            return False
        
        return True

    def load_data(self):
        """Load data from CSV into database."""
        print(f"📥 Loading data from {self.input_csv}...")
        
        try:
            with open(self.input_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                batch = []
                
                for row in reader:
                    self.stats['total_rows'] += 1
                    
                    # Validate row
                    if not self.validate_row(row):
                        self.stats['errors'] += 1
                        continue
                    
                    # Prepare row for insert
                    batch.append((
                        row['asset_id'],
                        row['file_id'],
                        row['file_name'],
                        row['file_type'],
                        row['mime_type'],
                        row['campaign_folder'],
                        row['tenant_id'],
                        row.get('size_bytes'),
                        row.get('modified_time'),
                        row.get('created_at', datetime.utcnow().isoformat()),
                        datetime.utcnow().isoformat()
                    ))
                    
                    # Insert batch if full
                    if len(batch) >= BATCH_SIZE:
                        self._insert_batch(batch)
                        batch = []
                
                # Insert remaining rows
                if batch:
                    self._insert_batch(batch)
                
                print("\n📊 Load Summary:")
                print(f"- Total rows processed: {self.stats['total_rows']}")
                print(f"- Successfully inserted: {self.stats['inserted']}")
                print(f"- Successfully updated: {self.stats['updated']}")
                print(f"- Errors: {self.stats['errors']}")
                
        except Exception as e:
            print(f"❌ Load failed: {str(e)}")
            raise

    def _insert_batch(self, batch: List[tuple]):
        """Insert a batch of rows."""
        try:
            execute_values(self.cursor, UPSERT_SQL, batch)
            self.stats['inserted'] += len(batch)
        except Exception as e:
            print(f"⚠️  Batch insert failed: {str(e)}")
            self.stats['errors'] += len(batch)

    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("👋 Database connection closed")

def main():
    loader = DatasetLoader(DATABASE_URL, INPUT_CSV)
    try:
        loader.connect()
        loader.create_table()
        loader.load_data()
    finally:
        loader.close()

if __name__ == "__main__":
    main() 