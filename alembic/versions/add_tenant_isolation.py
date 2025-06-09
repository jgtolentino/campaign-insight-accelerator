"""add tenant isolation

Revision ID: add_tenant_isolation
Revises: 20240320000000_ces_monitor
Create Date: 2024-03-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_tenant_isolation'
down_revision = '20240320000000_ces_monitor'
branch_labels = None
depends_on = None

def upgrade():
    # Add tenant_id column to sensors table
    op.add_column('sensors', sa.Column('tenant_id', sa.String(), nullable=False, server_default='scout'))
    
    # Add tenant_id column to sensor_metrics table
    op.add_column('sensor_metrics', sa.Column('tenant_id', sa.String(), nullable=False, server_default='scout'))
    
    # Add tenant_id column to model_status table
    op.add_column('model_status', sa.Column('tenant_id', sa.String(), nullable=False, server_default='scout'))
    
    # Add tenant_id column to retraining_jobs table
    op.add_column('retraining_jobs', sa.Column('tenant_id', sa.String(), nullable=False, server_default='scout'))

    # Create indexes
    op.create_index(op.f('ix_sensors_tenant_id'), 'sensors', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_sensor_metrics_tenant_id'), 'sensor_metrics', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_model_status_tenant_id'), 'model_status', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_retraining_jobs_tenant_id'), 'retraining_jobs', ['tenant_id'], unique=False)

    # Enable RLS
    op.execute('ALTER TABLE sensors ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE sensor_metrics ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE model_status ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE retraining_jobs ENABLE ROW LEVEL SECURITY')

    # Create RLS policies
    op.execute("""
        CREATE POLICY enforce_tenant_sensors ON sensors
        USING (tenant_id = current_setting('app.current_tenant', true))
    """)
    op.execute("""
        CREATE POLICY enforce_tenant_sensor_metrics ON sensor_metrics
        USING (tenant_id = current_setting('app.current_tenant', true))
    """)
    op.execute("""
        CREATE POLICY enforce_tenant_model_status ON model_status
        USING (tenant_id = current_setting('app.current_tenant', true))
    """)
    op.execute("""
        CREATE POLICY enforce_tenant_retraining_jobs ON retraining_jobs
        USING (tenant_id = current_setting('app.current_tenant', true))
    """)

def downgrade():
    # Drop RLS policies
    op.execute('DROP POLICY IF EXISTS enforce_tenant_sensors ON sensors')
    op.execute('DROP POLICY IF EXISTS enforce_tenant_sensor_metrics ON sensor_metrics')
    op.execute('DROP POLICY IF EXISTS enforce_tenant_model_status ON model_status')
    op.execute('DROP POLICY IF EXISTS enforce_tenant_retraining_jobs ON retraining_jobs')

    # Drop indexes
    op.drop_index(op.f('ix_sensors_tenant_id'), table_name='sensors')
    op.drop_index(op.f('ix_sensor_metrics_tenant_id'), table_name='sensor_metrics')
    op.drop_index(op.f('ix_model_status_tenant_id'), table_name='model_status')
    op.drop_index(op.f('ix_retraining_jobs_tenant_id'), table_name='retraining_jobs')

    # Remove tenant_id column from retraining_jobs table
    op.drop_column('retraining_jobs', 'tenant_id')
    
    # Remove tenant_id column from model_status table
    op.drop_column('model_status', 'tenant_id')
    
    # Remove tenant_id column from sensor_metrics table
    op.drop_column('sensor_metrics', 'tenant_id')
    
    # Remove tenant_id column from sensors table
    op.drop_column('sensors', 'tenant_id') 