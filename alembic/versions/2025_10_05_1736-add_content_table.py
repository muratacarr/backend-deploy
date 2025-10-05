"""Add content table

Revision ID: add_content_table
Revises: caac3dcfff84
Create Date: 2025-10-05 17:36:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_content_table'
down_revision = 'caac3dcfff84'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create contents table
    op.create_table('contents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False),
        sa.Column('is_moderated', sa.Boolean(), nullable=False),
        sa.Column('moderation_status', sa.String(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contents_id'), 'contents', ['id'], unique=False)
    op.create_index(op.f('ix_contents_title'), 'contents', ['title'], unique=False)
    op.create_index(op.f('ix_contents_author_id'), 'contents', ['author_id'], unique=False)
    op.create_index(op.f('ix_contents_created_at'), 'contents', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_contents_created_at'), table_name='contents')
    op.drop_index(op.f('ix_contents_author_id'), table_name='contents')
    op.drop_index(op.f('ix_contents_title'), table_name='contents')
    op.drop_index(op.f('ix_contents_id'), table_name='contents')
    op.drop_table('contents')
