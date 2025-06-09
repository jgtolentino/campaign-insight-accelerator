"""add tenant_id and enable RLS

Revision ID: 20240320000001_add_tenant_rls
Revises: 20240320000000_ces_monitor
Create Date: 2024-03-20 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240320000001_add_tenant_rls'
down_revision = '20240320000000_ces_monitor'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Add tenant_id columns (nullable for now)
    tables = ["sensors", "sensor_metrics", "model_status", "retraining_jobs"]
    for table in tables:
        op.add_column(
            table,
            sa.Column('tenant_id', sa.String(length=64), nullable=True, server_default='scout')
        )
        # Create index on tenant_id
        op.create_index(f'ix_{table}_tenant_id', table, ['tenant_id'])

    # 2. Make tenant_id non-nullable after backfill
    for table in tables:
        op.alter_column(
            table,
            'tenant_id',
            nullable=False,
            server_default=None  # Remove the default after making non-nullable
        )

    # 3. Enable RLS and create policy for each table
    for table in tables:
        # Enable row level security
        op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;')
        # Create enforce_tenant policy
        op.execute(
            f"""
            CREATE POLICY enforce_tenant_{table}
              ON {table}
              USING ( tenant_id = current_setting('app.current_tenant', true) );
            """
        )

def downgrade():
    # 1. Drop policies and disable RLS
    tables = ["sensors", "sensor_metrics", "model_status", "retraining_jobs"]
    for table in tables:
        op.execute(f'DROP POLICY IF EXISTS enforce_tenant_{table} ON {table};')
        op.execute(f'ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;')

    # 2. Drop indexes and columns
    for table in tables:
        op.drop_index(f'ix_{table}_tenant_id', table_name=table)
        op.drop_column(table, 'tenant_id') 