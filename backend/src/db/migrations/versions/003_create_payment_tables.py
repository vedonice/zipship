"""Create payment table migration."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    """Upgrade database schema."""
    op.create_table(
        'payments',
        sa.Column('payment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('processor_transaction_id', sa.String(255), nullable=True),
        sa.Column('idempotency_key', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('payment_id'),
        sa.UniqueConstraint('idempotency_key'),
    )
    op.create_index(op.f('ix_payments_order_id'), 'payments', ['order_id'], unique=False)


def downgrade():
    """Downgrade database schema."""
    op.drop_index(op.f('ix_payments_order_id'), table_name='payments')
    op.drop_table('payments')
