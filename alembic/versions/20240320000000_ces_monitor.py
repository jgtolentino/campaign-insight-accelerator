"""create CES monitor tables

Revision ID: 20240320000000_ces_monitor
Revises: 
Create Date: 2024-03-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240320000000_ces_monitor'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create sensors table
    op.create_table(
        'sensors',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # Create sensor_metrics table
    op.create_table(
        'sensor_metrics',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('sensor_id', sa.String(length=64), sa.ForeignKey('sensors.id'), nullable=False),
        sa.Column('metric_name', sa.String(length=255), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_sensor_metrics_sensor_id', 'sensor_metrics', ['sensor_id'])
    op.create_index('ix_sensor_metrics_timestamp', 'sensor_metrics', ['timestamp'])

    # Create model_status table
    op.create_table(
        'model_status',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('sensor_id', sa.String(length=64), sa.ForeignKey('sensors.id'), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('last_trained_at', sa.DateTime(), nullable=True),
        sa.Column('last_prediction_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_model_status_sensor_id', 'model_status', ['sensor_id'])

    # Create retraining_jobs table
    op.create_table(
        'retraining_jobs',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('sensor_id', sa.String(length=64), sa.ForeignKey('sensors.id'), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_retraining_jobs_sensor_id', 'retraining_jobs', ['sensor_id'])
    op.create_index('ix_retraining_jobs_status', 'retraining_jobs', ['status'])

def downgrade():
    op.drop_table('retraining_jobs')
    op.drop_table('model_status')
    op.drop_table('sensor_metrics')
    op.drop_table('sensors') 