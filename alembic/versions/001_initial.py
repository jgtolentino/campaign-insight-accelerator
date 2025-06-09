"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create agent_memory table
    op.create_table(
        'agent_memory',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('memory_type', sa.String(), nullable=False),
        sa.Column('content', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_memory_agent_id', 'agent_memory', ['agent_id'])
    op.create_index('ix_agent_memory_memory_type', 'agent_memory', ['memory_type'])

    # Create agent_message table
    op.create_table(
        'agent_message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.String(), nullable=False),
        sa.Column('receiver_id', sa.String(), nullable=False),
        sa.Column('message_type', sa.String(), nullable=False),
        sa.Column('content', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_message_sender_id', 'agent_message', ['sender_id'])
    op.create_index('ix_agent_message_receiver_id', 'agent_message', ['receiver_id'])
    op.create_index('ix_agent_message_message_type', 'agent_message', ['message_type'])

def downgrade():
    op.drop_table('agent_message')
    op.drop_table('agent_memory') 