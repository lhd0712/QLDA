"""merge avatar and event detail branches

Revision ID: c0425a72fc41
Revises: add_avatar_to_user, 010c9e942e7e
Create Date: 2025-06-06 12:41:22.370851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0425a72fc41'
down_revision = ('add_avatar_to_user', '010c9e942e7e')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
