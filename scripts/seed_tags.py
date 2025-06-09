#!/usr/bin/env python3
import os
import sys
import uuid
from datetime import datetime
from sqlalchemy import text

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_db

# Initial tags to seed
INITIAL_TAGS = [
    {
        "name": "Emotional Trigger",
        "description": "Content designed to evoke strong emotional responses"
    },
    {
        "name": "Brand Integration",
        "description": "Seamless incorporation of brand elements"
    },
    {
        "name": "Storytelling",
        "description": "Narrative-driven content"
    },
    {
        "name": "Product Showcase",
        "description": "Direct product demonstration or feature highlight"
    },
    {
        "name": "Social Proof",
        "description": "Customer testimonials or social validation"
    },
    {
        "name": "Call to Action",
        "description": "Clear directive for viewer engagement"
    },
    {
        "name": "Humor",
        "description": "Comedic elements or light-hearted content"
    },
    {
        "name": "Educational",
        "description": "Informative or instructional content"
    }
]

def seed_tags():
    """Seed initial tags and verify the tagging system."""
    print("🌱 Seeding initial tags...")

    # Get database session
    db = next(get_db())

    try:
        # Set tenant context (using 'scout' as default)
        db.execute(text("SET app.current_tenant = 'scout'"))

        # Insert tags
        for tag_data in INITIAL_TAGS:
            tag_id = str(uuid.uuid4())
            db.execute(
                text("""
                INSERT INTO tags (tag_id, name, description, tenant_id)
                VALUES (:tag_id, :name, :description, 'scout')
                """),
                {
                    "tag_id": tag_id,
                    "name": tag_data["name"],
                    "description": tag_data["description"]
                }
            )
        db.commit()

        # Verify tags were created
        print("\n🔍 Verifying tags...")
        tags = db.execute(text("SELECT * FROM tags ORDER BY name")).fetchall()
        print(f"Created {len(tags)} tags:")
        for tag in tags:
            print(f"- {tag.name}: {tag.description}")

        # Test RLS
        print("\n🔒 Testing tenant isolation...")
        # Try to access tags as a different tenant
        db.execute(text("SET app.current_tenant = 'agency123'"))
        other_tenant_tags = db.execute(text("SELECT * FROM tags")).fetchall()
        print(f"Tags visible to other tenant: {len(other_tenant_tags)}")

        # Switch back to scout tenant
        db.execute(text("SET app.current_tenant = 'scout'"))
        scout_tags = db.execute(text("SELECT * FROM tags")).fetchall()
        print(f"Tags visible to scout tenant: {len(scout_tags)}")

        print("\n✅ Tag seeding complete!")

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_tags() 