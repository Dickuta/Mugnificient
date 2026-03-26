from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.data.database import get_db
from app.core.security import get_current_user
from app.core.utils.rbac import require_permission, Permissions, has_permission
from app.models.models import User, Role, Permission as PermissionModel, UserRole


router = APIRouter(prefix="/rbac", tags=["rbac"])


class RoleCreate(BaseModel):
    name: str
    description: str = ""
    is_default: bool = False
    permissions: List[str] = []


class RoleUpdate(BaseModel):
    description: Optional[str] = None
    is_default: Optional[bool] = None
    permissions: Optional[List[str]] = None


class PermissionCreate(BaseModel):
    name: str
    description: str = ""


class UserRoleUpdate(BaseModel):
    role_id: int


# Permissions
@router.get("/permissions")
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_PERMISSIONS)),
):
    perms = db.query(PermissionModel).all()
    return [{"id": p.id, "name": p.name, "description": p.description} for p in perms]


@router.post("/permissions")
def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_PERMISSIONS)),
):
    existing = (
        db.query(PermissionModel)
        .filter(PermissionModel.name == permission.name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists")

    perm = PermissionModel(name=permission.name, description=permission.description)
    db.add(perm)
    db.commit()
    db.refresh(perm)

    return {"id": perm.id, "name": perm.name}


# Roles
@router.get("/roles")
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_ROLES)),
):
    roles = db.query(Role).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "is_default": r.is_default,
            "permissions": [p.name for p in r.permissions],
        }
        for r in roles
    ]


@router.post("/roles")
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_ROLES)),
):
    existing = db.query(Role).filter(Role.name == role.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")

    # Get permission objects
    perms = (
        db.query(PermissionModel)
        .filter(PermissionModel.name.in_(role.permissions))
        .all()
        if role.permissions
        else []
    )

    # Handle default role
    if role.is_default:
        db.query(Role).update({Role.is_default: False})

    new_role = Role(
        name=role.name,
        description=role.description,
        is_default=role.is_default,
        permissions=perms,
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return {"id": new_role.id, "name": new_role.name}


@router.put("/roles/{role_id}")
def update_role(
    role_id: int,
    role: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_ROLES)),
):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.description is not None:
        db_role.description = role.description

    if role.is_default is not None:
        if role.is_default:
            db.query(Role).filter(Role.id != role_id).update({Role.is_default: False})
        db_role.is_default = role.is_default

    if role.permissions is not None:
        perms = (
            db.query(PermissionModel)
            .filter(PermissionModel.name.in_(role.permissions))
            .all()
        )
        db_role.permissions = perms

    db.commit()
    return {"message": "Role updated"}


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_ROLES)),
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default role")

    # Remove role from users
    db.query(UserRole).filter(UserRole.role_id == role_id).delete()

    db.delete(role)
    db.commit()
    return {"message": "Role deleted"}


# User Roles
@router.get("/users/{user_id}/roles")
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_ROLES)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "username": user.username,
        "role": {
            "id": user.role.id,
            "name": user.role.name,
            "permissions": [p.name for p in user.role.permissions],
        }
        if user.role
        else None,
        "is_staff": user.is_staff,
    }


@router.put("/users/{user_id}/roles")
def assign_user_role(
    user_id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_ROLES)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.id == data.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    user.role_id = role.id
    db.commit()

    return {"message": f"Role '{role.name}' assigned to user {user.username}"}


@router.put("/users/{user_id}/staff")
def set_staff_status(
    user_id: int,
    is_staff: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_ROLES)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_staff = is_staff
    db.commit()

    return {"message": f"Staff status set to {is_staff} for {user.username}"}


# Check permissions
@router.get("/my-permissions")
def get_my_permissions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    from app.core.utils.rbac import get_user_permissions

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "is_staff": current_user.is_staff,
        "role": current_user.role.name if current_user.role else None,
        "permissions": get_user_permissions(current_user),
    }


@router.post("/seed-defaults")
def seed_default_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permissions.MANAGE_PERMISSIONS)),
):
    """Seed default permissions and roles"""

    # Permissions
    default_permissions = [
        ("view_products", "View products"),
        ("create_products", "Create products"),
        ("edit_products", "Edit products"),
        ("delete_products", "Delete products"),
        ("view_orders", "View orders"),
        ("create_orders", "Create orders"),
        ("edit_orders", "Edit orders"),
        ("delete_orders", "Delete orders"),
        ("view_users", "View users"),
        ("create_users", "Create users"),
        ("edit_users", "Edit users"),
        ("delete_users", "Delete users"),
        ("view_inventory", "View inventory"),
        ("manage_inventory", "Manage inventory"),
        ("view_stock_alerts", "View stock alerts"),
        ("manage_suppliers", "Manage suppliers"),
        ("view_reports", "View reports"),
        ("view_analytics", "View analytics"),
        ("manage_roles", "Manage roles"),
        ("manage_permissions", "Manage permissions"),
        ("view_categories", "View categories"),
        ("manage_categories", "Manage categories"),
    ]

    for name, desc in default_permissions:
        existing = (
            db.query(PermissionModel).filter(PermissionModel.name == name).first()
        )
        if not existing:
            perm = PermissionModel(name=name, description=desc)
            db.add(perm)

    # Roles
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(
            name="admin", description="Administrator with all permissions"
        )
        db.add(admin_role)
        db.flush()
        admin_role.permissions = db.query(PermissionModel).all()

    manager_role = db.query(Role).filter(Role.name == "manager").first()
    if not manager_role:
        manager_perms = [
            "view_products",
            "create_products",
            "edit_products",
            "view_orders",
            "edit_orders",
            "view_inventory",
            "manage_inventory",
            "view_stock_alerts",
            "manage_suppliers",
            "view_reports",
            "view_analytics",
            "view_categories",
            "manage_categories",
        ]
        perms = (
            db.query(PermissionModel)
            .filter(PermissionModel.name.in_(manager_perms))
            .all()
        )
        manager_role = Role(
            name="manager", description="Store manager", permissions=perms
        )
        db.add(manager_role)

    staff_role = db.query(Role).filter(Role.name == "staff").first()
    if not staff_role:
        staff_perms = [
            "view_products",
            "view_orders",
            "create_orders",
            "view_inventory",
            "view_categories",
        ]
        perms = (
            db.query(PermissionModel)
            .filter(PermissionModel.name.in_(staff_perms))
            .all()
        )
        staff_role = Role(name="staff", description="Store staff", permissions=perms)
        db.add(staff_role)

    customer_role = db.query(Role).filter(Role.name == "customer").first()
    if not customer_role:
        customer_role = Role(
            name="customer", description="Customer role", is_default=True
        )
        db.add(customer_role)

    db.commit()
    return {"message": "Default permissions and roles seeded"}
