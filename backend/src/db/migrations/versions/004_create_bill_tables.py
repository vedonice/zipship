"""Create bill table migration."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    """Upgrade database schema."""
    op.create_table(
        'bills',
        sa.Column('bill_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bill_number', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('items_json', sa.Text(), nullable=False),
        sa.Column('subtotal', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('shipping_fee', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('bill_id'),
        sa.UniqueConstraint('bill_number'),
        sa.UniqueConstraint('order_id'),
    )
    op.create_index(op.f('ix_bills_order_id'), 'bills', ['order_id'], unique=False)


def downgrade():
    """Downgrade database schema."""
    op.drop_index(op.f('ix_bills_order_id'), table_name='bills')
    op.drop_table('bills')
