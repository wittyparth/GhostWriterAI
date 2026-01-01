"""Initial migration - create all tables

Revision ID: 001
Revises: 
Create Date: 2025-12-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=True),
        sa.Column('linkedin_profile_url', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    # Brand profiles table
    op.create_table(
        'brand_profiles',
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id'), unique=True, nullable=False),
        sa.Column('content_pillars', postgresql.JSONB, default=[]),
        sa.Column('target_audience', sa.Text, nullable=True),
        sa.Column('brand_voice', sa.Text, nullable=True),
        sa.Column('tone_preferences', postgresql.JSONB, default={}),
        sa.Column('unique_positioning', sa.Text, nullable=True),
        sa.Column('visual_guidelines', postgresql.JSONB, default={}),
        sa.Column('brand_colors', postgresql.JSONB, default=[]),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    # Posts table
    op.create_table(
        'posts',
        sa.Column('post_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('raw_idea', sa.Text, nullable=False),
        sa.Column('final_content', sa.Text, nullable=True),
        sa.Column('format', sa.String(50), nullable=True),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('structure_type', sa.String(100), nullable=True),
        sa.Column('tone', sa.String(100), nullable=True),
        sa.Column('content_pillar', sa.String(100), nullable=True),
        sa.Column('hook_type', sa.String(100), nullable=True),
        sa.Column('hooks_generated', postgresql.JSONB, default=[]),
        sa.Column('selected_hook_index', sa.Integer, nullable=True),
        sa.Column('visual_specs', postgresql.JSONB, default={}),
        sa.Column('impressions', sa.Integer, nullable=True),
        sa.Column('engagement_rate', sa.Float, nullable=True),
        sa.Column('comments_count', sa.Integer, nullable=True),
        sa.Column('reactions_count', sa.Integer, nullable=True),
        sa.Column('shares_count', sa.Integer, nullable=True),
        sa.Column('saves_count', sa.Integer, nullable=True),
        sa.Column('quality_score', sa.Float, nullable=True),
        sa.Column('predicted_impressions_min', sa.Integer, nullable=True),
        sa.Column('predicted_impressions_max', sa.Integer, nullable=True),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('generation_version', sa.Integer, default=1),
        sa.Column('optimization_suggestions', postgresql.JSONB, default=[]),
        sa.Column('published_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    
    # Reference posts table
    op.create_table(
        'reference_posts',
        sa.Column('ref_post_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source', sa.String(50), default='manual'),
        sa.Column('creator_name', sa.String(255), nullable=True),
        sa.Column('creator_profile_url', sa.Text, nullable=True),
        sa.Column('original_url', sa.Text, nullable=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('format', sa.String(50), nullable=True),
        sa.Column('structure_type', sa.String(100), nullable=True),
        sa.Column('hook_type', sa.String(100), nullable=True),
        sa.Column('hook_text', sa.Text, nullable=True),
        sa.Column('impressions', sa.Integer, nullable=True),
        sa.Column('engagement_rate', sa.Float, nullable=True),
        sa.Column('comments_count', sa.Integer, nullable=True),
        sa.Column('reactions_count', sa.Integer, nullable=True),
        sa.Column('niche', sa.String(100), nullable=True),
        sa.Column('content_pillar', sa.String(100), nullable=True),
        sa.Column('psychological_triggers', postgresql.JSONB, default=[]),
        sa.Column('tone', sa.String(100), nullable=True),
        sa.Column('hook_score', sa.Float, nullable=True),
        sa.Column('value_density_score', sa.Float, nullable=True),
        sa.Column('why_it_works', sa.Text, nullable=True),
        sa.Column('replicable_pattern', sa.Text, nullable=True),
        sa.Column('embedding_id', sa.String(255), nullable=True),
        sa.Column('original_post_date', sa.DateTime, nullable=True),
        sa.Column('scraped_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    
    # Agent executions table
    op.create_table(
        'agent_executions',
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.post_id'), nullable=True),
        sa.Column('agent_name', sa.String(100), nullable=False),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('input_data', postgresql.JSONB, default={}),
        sa.Column('output_data', postgresql.JSONB, default={}),
        sa.Column('execution_time_ms', sa.Integer, nullable=True),
        sa.Column('input_tokens', sa.Integer, nullable=True),
        sa.Column('output_tokens', sa.Integer, nullable=True),
        sa.Column('cost_usd', sa.Float, nullable=True),
        sa.Column('status', sa.String(50), default='success'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    
    # User feedback table
    op.create_table(
        'user_feedback',
        sa.Column('feedback_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.post_id'), nullable=False),
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agent_executions.execution_id'), nullable=True),
        sa.Column('feedback_type', sa.String(50), nullable=False),
        sa.Column('rating', sa.Integer, nullable=True),
        sa.Column('comments', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    
    # Create indexes
    op.create_index('ix_posts_user_id', 'posts', ['user_id'])
    op.create_index('ix_posts_status', 'posts', ['status'])
    op.create_index('ix_reference_posts_niche', 'reference_posts', ['niche'])
    op.create_index('ix_reference_posts_engagement', 'reference_posts', ['engagement_rate'])
    op.create_index('ix_agent_executions_post_id', 'agent_executions', ['post_id'])


def downgrade() -> None:
    op.drop_index('ix_agent_executions_post_id')
    op.drop_index('ix_reference_posts_engagement')
    op.drop_index('ix_reference_posts_niche')
    op.drop_index('ix_posts_status')
    op.drop_index('ix_posts_user_id')
    
    op.drop_table('user_feedback')
    op.drop_table('agent_executions')
    op.drop_table('reference_posts')
    op.drop_table('posts')
    op.drop_table('brand_profiles')
    op.drop_table('users')
