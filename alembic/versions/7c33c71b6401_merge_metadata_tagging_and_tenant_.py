"""Merge metadata tagging and tenant isolation heads

Revision ID: 7c33c71b6401
Revises: 20240320000002_add_metadata_tagging, add_tenant_isolation
Create Date: 2025-06-08 15:24:22.310433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c33c71b6401'
down_revision = ('20240320000002_add_metadata_tagging', 'add_tenant_isolation')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass 