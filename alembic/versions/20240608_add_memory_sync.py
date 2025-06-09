"""Add memory sync tables

Revision ID: 20240608_memory_sync
Revises: 
Create Date: 2024-06-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240608_memory_sync'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Agent memory table
    op.create_table(
        'agent_memory',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('memory_type', sa.String(), nullable=False),
        sa.Column('content', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_memory_agent_id', 'agent_memory', ['agent_id'])
    op.create_index('ix_agent_memory_memory_type', 'agent_memory', ['memory_type'])

    # Cross-agent communication table
    op.create_table(
        'agent_communication',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.String(), nullable=False),
        sa.Column('receiver_id', sa.String(), nullable=False),
        sa.Column('message_type', sa.String(), nullable=False),
        sa.Column('content', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_communication_sender_id', 'agent_communication', ['sender_id'])
    op.create_index('ix_agent_communication_receiver_id', 'agent_communication', ['receiver_id'])

def downgrade():
    op.drop_table('agent_communication')
    op.drop_table('agent_memory') 