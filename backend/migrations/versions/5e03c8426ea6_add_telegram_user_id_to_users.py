"""add_telegram_user_id_to_users

Revision ID: 5e03c8426ea6
Revises: a83deb300732
Create Date: 2025-09-16 14:40:55.575744

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e03c8426ea6'
down_revision = 'a83deb300732'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add telegram_user_id column to users table
    op.add_column('users', sa.Column('telegram_user_id', sa.BigInteger(), nullable=True))
    op.create_index(op.f('ix_users_telegram_user_id'), 'users', ['telegram_user_id'], unique=True)


def downgrade() -> None:
    # Remove telegram_user_id column from users table
    op.drop_index(op.f('ix_users_telegram_user_id'), table_name='users')
    op.drop_column('users', 'telegram_user_id')
