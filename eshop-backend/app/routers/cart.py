from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Cart, CartItem, Product

router = APIRouter(prefix="/cart", tags=["cart"])


def get_or_create_cart(db: Session, user_id: int = None, session_key: str = None):
    if user_id:
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
    elif session_key:
        cart = db.query(Cart).filter(Cart.session_key == session_key).first()
        if not cart:
            cart = Cart(session_key=session_key)
            db.add(cart)
            db.commit()
            db.refresh(cart)
    else:
        cart = Cart()
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


@router.get("/")
def get_cart(
    user_id: int = None, session_key: str = None, db: Session = Depends(get_db)
):
    cart = get_or_create_cart(db, user_id, session_key)

    items = []
    total_price = 0
    total_items = 0

    for item in cart.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product and product.is_active:
            item_total = float(product.price) * item.quantity
            items.append(
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": product.name,
                    "product_image": product.image,
                    "product_price": float(product.price),
                    "quantity": item.quantity,
                    "item_total": item_total,
                }
            )
            total_price += item_total
            total_items += item.quantity

    return {
        "id": cart.id,
        "items": items,
        "total_items": total_items,
        "total_price": round(total_price, 2),
    }


@router.post("/add")
def add_to_cart(
    product_id: int,
    quantity: int = 1,
    user_id: int = None,
    session_key: str = None,
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    cart = get_or_create_cart(db, user_id, session_key)

    cart_item = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        .first()
    )

    if cart_item:
        new_quantity = cart_item.quantity + quantity
        cart_item.quantity = min(new_quantity, product.stock)
        db.commit()
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(cart_item)
        db.commit()

    return {"message": "Item added to cart", "cart_id": cart.id}


@router.put("/item/{item_id}")
def update_cart_item(item_id: int, quantity: int, db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found")

    product = db.query(Product).filter(Product.id == cart_item.product_id).first()

    if quantity > product.stock:
        raise HTTPException(
            status_code=400, detail=f"Only {product.stock} items available"
        )

    if quantity > 0:
        cart_item.quantity = quantity
        db.commit()
    else:
        db.delete(cart_item)
        db.commit()

    return {"message": "Cart updated"}


@router.delete("/item/{item_id}")
def remove_from_cart(item_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.delete("/clear")
def clear_cart(
    user_id: int = None, session_key: str = None, db: Session = Depends(get_db)
):
    cart = get_or_create_cart(db, user_id, session_key)
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return {"message": "Cart cleared"}
