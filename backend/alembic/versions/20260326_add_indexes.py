"""Add database indexes for performance

Revision ID: indexes001
Revises: forecasting001
Create Date: 2026-03-26

"""
from alembic import op
import sqlalchemy as sa

revision = 'indexes001'
down_revision = 'forecasting001'
branch_labels = None
depends_on = None


def upgrade():
    # Sales history indexes
    op.create_index('ix_sales_history_product_date', 'sales_history', ['product_id', 'date'])
    op.create_index('ix_sales_history_date', 'sales_history', ['date'])
    
    # Forecast indexes
    op.create_index('ix_forecasts_product_date', 'forecasts', ['product_id', 'forecast_date'])
    op.create_index('ix_forecasts_created', 'forecasts', ['created_at'])
    
    # Seasonal patterns
    op.create_index('ix_seasonal_product_month', 'seasonal_patterns', ['product_id', 'month'], unique=True)
    
    # Purchase orders
    op.create_index('ix_purchase_orders_status', 'purchase_orders', ['status'])
    op.create_index('ix_purchase_orders_supplier', 'purchase_orders', ['supplier_id'])
    op.create_index('ix_purchase_orders_created', 'purchase_orders', ['created_at'])
    
    # Refill requests
    op.create_index('ix_refill_requests_status', 'refill_requests', ['status'])
    op.create_index('ix_refill_requests_product', 'refill_requests', ['product_id'])
    op.create_index('ix_refill_requests_supplier', 'refill_requests', ['supplier_id'])
    
    # Auto order settings
    op.create_index('ix_auto_order_settings_product', 'auto_order_settings', ['product_id'], unique=True)
    
    # Stock movements (if exists)
    if op.has_table('stock_movements'):
        op.create_index('ix_stock_movements_product', 'stock_movements', ['stock_item_id'])
        op.create_index('ix_stock_movements_date', 'stock_movements', ['created_at'])


def downgrade():
    op.drop_index('ix_auto_order_settings_product', table_name='auto_order_settings')
    op.drop_index('ix_refill_requests_supplier', table_name='refill_requests')
    op.drop_index('ix_refill_requests_product', table_name='refill_requests')
    op.drop_index('ix_refill_requests_status', table_name='refill_requests')
    op.drop_index('ix_purchase_orders_created', table_name='purchase_orders')
    op.drop_index('ix_purchase_orders_supplier', table_name='purchase_orders')
    op.drop_index('ix_purchase_orders_status', table_name='purchase_orders')
    op.drop_index('ix_seasonal_product_month', table_name='seasonal_patterns')
    op.drop_index('ix_forecasts_created', table_name='forecasts')
    op.drop_index('ix_forecasts_product_date', table_name='forecasts')
    op.drop_index('ix_sales_history_date', table_name='sales_history')
    op.drop_index('ix_sales_history_product_date', table_name='sales_history')
    
    if op.has_table('stock_movements'):
        op.drop_index('ix_stock_movements_date', table_name='stock_movements')
        op.drop_index('ix_stock_movements_product', table_name='stock_movements')
