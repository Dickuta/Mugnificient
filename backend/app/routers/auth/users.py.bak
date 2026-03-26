from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import User, Address
from app.schemas.schemas import UserResponse, UserUpdate, AddressCreate, AddressResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}/addresses", response_model=List[AddressResponse])
def list_addresses(user_id: int, db: Session = Depends(get_db)):
    addresses = db.query(Address).filter(Address.user_id == user_id).all()
    return addresses


@router.post("/{user_id}/addresses", response_model=AddressResponse)
def create_address(user_id: int, address: AddressCreate, db: Session = Depends(get_db)):
    if address.is_default:
        db.query(Address).filter(Address.user_id == user_id).update(
            {"is_default": False}
        )

    db_address = Address(**address.dict(), user_id=user_id)
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


@router.put("/addresses/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int, address: AddressCreate, db: Session = Depends(get_db)
):
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")

    if address.is_default:
        db.query(Address).filter(
            Address.user_id == db_address.user_id, Address.id != address_id
        ).update({"is_default": False})

    for key, value in address.dict().items():
        setattr(db_address, key, value)

    db.commit()
    db.refresh(db_address)
    return db_address


@router.delete("/addresses/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(db_address)
    db.commit()
    return {"message": "Address deleted"}
