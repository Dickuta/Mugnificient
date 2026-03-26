"""Add forecasting and auto-order models

Revision ID: forecasting001
Revises: f75982300713_initial_migration
Create Date: 2026-03-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'forecasting001'
down_revision = 'f75982300713_initial_migration'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'seasonal_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('demand_multiplier', sa.DECIMAL(5, 2), default=1.0),
        sa.Column('notes', sa.Text(), default=''),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    
    op.create_table(
        'sales_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('quantity_sold', sa.Integer(), default=0),
        sa.Column('revenue', sa.DECIMAL(10, 2), default=0),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    
    op.create_index(op.f('ix_sales_history_date'), 'sales_history', ['date'])
    op.create_index(op.f('ix_sales_history_product_id'), 'sales_history', ['product_id'])
    
    op.create_table(
        'forecasts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('forecast_date', sa.DateTime(), nullable=False),
        sa.Column('predicted_quantity', sa.Integer(), nullable=False),
        sa.Column('confidence_low', sa.Integer(), default=0),
        sa.Column('confidence_high', sa.Integer(), default=0),
        sa.Column('is_auto_order', sa.Boolean(), default=False),
        sa.Column('auto_order_created', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    
    op.create_index(op.f('ix_forecasts_product_id'), 'forecasts', ['product_id'])
    op.create_index(op.f('ix_forecasts_forecast_date'), 'forecasts', ['forecast_date'])
    
    op.create_table(
        'purchase_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(20), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('total_amount', sa.DECIMAL(10, 2), default=0),
        sa.Column('notes', sa.Text(), default=''),
        sa.Column('expected_delivery', sa.DateTime(), nullable=True),
        sa.Column('is_auto_generated', sa.Boolean(), default=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number'),
    )
    
    op.create_table(
        'purchase_order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_cost', sa.DECIMAL(10, 2), default=0),
        sa.Column('received_quantity', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    
    op.create_table(
        'auto_order_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), default=False),
        sa.Column('min_stock_threshold', sa.Integer(), default=10),
        sa.Column('order_quantity', sa.Integer(), default=50),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id'),
    )

    op.create_table(
        'refill_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=True),
        sa.Column('quantity_requested', sa.Integer(), default=0),
        sa.Column('quantity_fulfilled', sa.Integer(), default=0),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('estimated_cost', sa.DECIMAL(10, 2), default=0),
        sa.Column('actual_cost', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('notes', sa.Text(), default=''),
        sa.Column('requested_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('ordered_at', sa.DateTime(), nullable=True),
        sa.Column('received_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('refill_requests')
    op.drop_table('auto_order_settings')
    op.drop_table('purchase_order_items')
    op.drop_table('purchase_orders')
    op.drop_table('forecasts')
    op.drop_table('sales_history')
    op.drop_table('seasonal_patterns')
