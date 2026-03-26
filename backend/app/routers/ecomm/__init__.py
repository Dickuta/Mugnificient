from .products import router as products
from .categories import router as categories
from .cart import router as cart
from .orders import router as orders
from .recommendations import router as recommendations

__all__ = ['products', 'categories', 'cart', 'orders', 'recommendations']