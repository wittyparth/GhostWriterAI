"""Add generation history tables

Revision ID: 002_generation_history
Revises: 001_initial
Create Date: 2026-01-01 15:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_generation_history'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create generation_history table
    op.create_table(
        'generation_history',
        sa.Column('history_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.post_id'), nullable=False, unique=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id'), nullable=True),
        
        # Input data
        sa.Column('raw_idea', sa.Text(), nullable=False),
        sa.Column('preferred_format', sa.String(50), nullable=True),
        sa.Column('brand_profile_snapshot', postgresql.JSONB(), server_default='{}'),
        
        # Agent outputs
        sa.Column('validator_output', postgresql.JSONB(), server_default='{}'),
        sa.Column('strategist_output', postgresql.JSONB(), server_default='{}'),
        sa.Column('writer_output', postgresql.JSONB(), server_default='{}'),
        sa.Column('visual_output', postgresql.JSONB(), server_default='{}'),
        sa.Column('optimizer_output', postgresql.JSONB(), server_default='{}'),
        
        # User interaction
        sa.Column('clarifying_questions', postgresql.JSONB(), server_default='[]'),
        sa.Column('user_answers', postgresql.JSONB(), server_default='{}'),
        
        # Final output
        sa.Column('final_post', postgresql.JSONB(), server_default='{}'),
        sa.Column('selected_hook_index', sa.Integer(), server_default='0'),
        
        # Execution metadata
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('total_execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('revision_count', sa.Integer(), server_default='0'),
        
        # Agent timing
        sa.Column('validator_time_ms', sa.Integer(), nullable=True),
        sa.Column('strategist_time_ms', sa.Integer(), nullable=True),
        sa.Column('writer_time_ms', sa.Integer(), nullable=True),
        sa.Column('visual_time_ms', sa.Integer(), nullable=True),
        sa.Column('optimizer_time_ms', sa.Integer(), nullable=True),
        
        # Error handling
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('failed_agent', sa.String(100), nullable=True),
        
        # Timestamps
        sa.Column('started_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('phase1_completed_at', sa.DateTime(), nullable=True),
        sa.Column('answers_submitted_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    
    # Create indexes for common queries
    op.create_index('ix_generation_history_post_id', 'generation_history', ['post_id'])
    op.create_index('ix_generation_history_user_id', 'generation_history', ['user_id'])
    op.create_index('ix_generation_history_status', 'generation_history', ['status'])
    op.create_index('ix_generation_history_started_at', 'generation_history', ['started_at'])
    
    # Create generation_events table
    op.create_table(
        'generation_events',
        sa.Column('event_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('history_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('generation_history.history_id'), nullable=False),
        
        # Event details
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('agent_name', sa.String(100), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        
        # Event data
        sa.Column('execution_time_ms', sa.Integer(), server_default='0'),
        sa.Column('progress_percent', sa.Integer(), server_default='0'),
        
        # Output summary
        sa.Column('output_summary', sa.Text(), nullable=True),
        sa.Column('decision', sa.String(50), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        
        # Full event data
        sa.Column('event_data', postgresql.JSONB(), server_default='{}'),
        
        # Error info
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_attempt', sa.Integer(), nullable=True),
        
        # Timestamp
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes for events
    op.create_index('ix_generation_events_history_id', 'generation_events', ['history_id'])
    op.create_index('ix_generation_events_timestamp', 'generation_events', ['timestamp'])
    op.create_index('ix_generation_events_event_type', 'generation_events', ['event_type'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_generation_events_event_type', table_name='generation_events')
    op.drop_index('ix_generation_events_timestamp', table_name='generation_events')
    op.drop_index('ix_generation_events_history_id', table_name='generation_events')
    
    op.drop_index('ix_generation_history_started_at', table_name='generation_history')
    op.drop_index('ix_generation_history_status', table_name='generation_history')
    op.drop_index('ix_generation_history_user_id', table_name='generation_history')
    op.drop_index('ix_generation_history_post_id', table_name='generation_history')
    
    # Drop tables
    op.drop_table('generation_events')
    op.drop_table('generation_history')
