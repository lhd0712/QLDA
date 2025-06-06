"""add avatar field to user

Revision ID: add_avatar_to_user
Revises: 82803415e43a
Create Date: 2025-06-06

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_avatar_to_user'
down_revision = '82803415e43a'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('user', sa.Column('avatar', sa.String(length=255), nullable=True))

def downgrade():
    op.drop_column('user', 'avatar')
