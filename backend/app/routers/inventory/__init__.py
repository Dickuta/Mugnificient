from .inventory import router as inventory
from .forecasting import router as forecasting
from .inventory_ml import router as inventory_ml

__all__ = ['inventory', 'forecasting', 'inventory_ml']