"""add metadata tagging tables

Revision ID: 20240320000002_add_metadata_tagging
Revises: 20240320000001_add_tenant_rls
Create Date: 2024-03-20 00:00:02.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240320000002_add_metadata_tagging'
down_revision = '20240320000001_add_tenant_rls'
branch_labels = None
depends_on = None


def upgrade():
    # 1. tags master table
    op.create_table(
        'tags',
        sa.Column('tag_id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('tenant_id', sa.String(length=64), nullable=False)  # Add tenant_id for RLS
    )
    op.create_index('ix_tags_tenant_id', 'tags', ['tenant_id'])

    # 2. campaign_tags association
    op.create_table(
        'campaign_tags',
        sa.Column('campaign_id', sa.String(length=36), sa.ForeignKey('campaigns.campaign_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', sa.String(length=36), sa.ForeignKey('tags.tag_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),  # Add tenant_id for RLS
        sa.UniqueConstraint('campaign_id', 'tag_id', name='uq_campaign_tag')
    )
    op.create_index('ix_campaign_tags_tag_id', 'campaign_tags', ['tag_id'])
    op.create_index('ix_campaign_tags_tenant_id', 'campaign_tags', ['tenant_id'])

    # 3. asset_tags association
    op.create_table(
        'asset_tags',
        sa.Column('asset_id', sa.String(length=36), sa.ForeignKey('assets.asset_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', sa.String(length=36), sa.ForeignKey('tags.tag_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),  # Add tenant_id for RLS
        sa.UniqueConstraint('asset_id', 'tag_id', name='uq_asset_tag')
    )
    op.create_index('ix_asset_tags_tag_id', 'asset_tags', ['tag_id'])
    op.create_index('ix_asset_tags_tenant_id', 'asset_tags', ['tenant_id'])

    # Enable RLS and create policies for new tables
    for table in ['tags', 'campaign_tags', 'asset_tags']:
        op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;')
        op.execute(
            f"""
            CREATE POLICY enforce_tenant_{table}
              ON {table}
              USING ( tenant_id = current_setting('app.current_tenant', true) );
            """
        )


def downgrade():
    # Drop RLS policies first
    for table in ['tags', 'campaign_tags', 'asset_tags']:
        op.execute(f'DROP POLICY IF EXISTS enforce_tenant_{table} ON {table};')
        op.execute(f'ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;')

    # Drop tables in reverse order
    op.drop_index('ix_asset_tags_tenant_id', table_name='asset_tags')
    op.drop_index('ix_asset_tags_tag_id', table_name='asset_tags')
    op.drop_table('asset_tags')

    op.drop_index('ix_campaign_tags_tenant_id', table_name='campaign_tags')
    op.drop_index('ix_campaign_tags_tag_id', table_name='campaign_tags')
    op.drop_table('campaign_tags')

    op.drop_index('ix_tags_tenant_id', table_name='tags')
    op.drop_table('tags') 