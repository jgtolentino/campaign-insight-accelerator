#!/usr/bin/env python3
import os
import sys
import csv
import uuid
from datetime import datetime
from sqlalchemy import text

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_db

def import_tags_from_csv(csv_path: str, tenant_id: str = 'scout'):
    """Import tags from a CSV file.
    
    CSV should have columns: name,description
    """
    print(f"📥 Importing tags from {csv_path}...")

    # Get database session
    db = next(get_db())

    try:
        # Set tenant context
        db.execute(text(f"SET app.current_tenant = '{tenant_id}'"))

        # Read and import tags
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            imported = 0
            skipped = 0
            
            for row in reader:
                # Check if tag already exists
                existing = db.execute(
                    text("SELECT tag_id FROM tags WHERE name = :name"),
                    {"name": row["name"]}
                ).fetchone()
                
                if existing:
                    print(f"⏭️  Skipping existing tag: {row['name']}")
                    skipped += 1
                    continue
                
                # Create new tag
                tag_id = str(uuid.uuid4())
                db.execute(
                    text("""
                    INSERT INTO tags (tag_id, name, description, tenant_id)
                    VALUES (:tag_id, :name, :description, :tenant_id)
                    """),
                    {
                        "tag_id": tag_id,
                        "name": row["name"],
                        "description": row.get("description"),
                        "tenant_id": tenant_id
                    }
                )
                print(f"✅ Imported tag: {row['name']}")
                imported += 1
            
            db.commit()
            print(f"\n📊 Import Summary:")
            print(f"- Imported: {imported} tags")
            print(f"- Skipped: {skipped} existing tags")
            print(f"- Total: {imported + skipped} tags processed")

    except Exception as e:
        print(f"\n❌ Error during import: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./import_tags.py <csv_file> [tenant_id]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    tenant_id = sys.argv[2] if len(sys.argv) > 2 else 'scout'
    
    import_tags_from_csv(csv_path, tenant_id) 