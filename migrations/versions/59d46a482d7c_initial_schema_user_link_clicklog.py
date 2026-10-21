
"""Initial schema: User, Link, ClickLog

Revision ID: 59d46a482d7c
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = '59d46a482d7c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create User first because Link references User.
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        'ix_user_username', 'user', ['username'], unique=True
    )
    op.create_index(
        'ix_user_email', 'user', ['email'], unique=True
    )

    # 2. Create Link after User.
    op.create_table(
        'link',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('original_url', sa.String(length=2048), nullable=False),
        sa.Column('short_code', sa.String(length=20), nullable=False),
        sa.Column('clicks', sa.Integer(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('expiry', sa.DateTime(), nullable=True),
        sa.Column('password', sa.String(length=256), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        'ix_link_short_code', 'link', ['short_code'], unique=True
    )

    # 3. Create ClickLog after Link.
    op.create_table(
        'click_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('link_id', sa.Integer(), nullable=False),
        sa.Column('clicked_at', sa.DateTime(), nullable=True),
        sa.Column('referrer', sa.String(length=500), nullable=True),
        sa.Column(
            'user_agent_category', sa.String(length=50), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ['link_id'], ['link.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('click_log')

    op.drop_index('ix_link_short_code', table_name='link')
    op.drop_table('link')

    op.drop_index('ix_user_email', table_name='user')
    op.drop_index('ix_user_username', table_name='user')
    op.drop_table('user')
