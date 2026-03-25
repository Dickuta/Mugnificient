from functools import wraps
from fastapi import HTTPException, Depends
from typing import List, Optional
import re

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Role, Permission


# Input validation patterns
SAFE_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,50}$")
SAFE_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def sanitize_input(value: str, max_length: int = 255) -> str:
    """Sanitize user input"""
    if not value:
        return value

    # Trim whitespace
    value = value.strip()

    # Limit length
    if len(value) > max_length:
        value = value[:max_length]

    return value


def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username:
        return False
    return bool(SAFE_USERNAME_PATTERN.match(username))


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    return bool(SAFE_EMAIL_PATTERN.match(email))


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if not password:
        return False, "Password is required"

    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    if len(password) > 128:
        return False, "Password is too long"

    return True, ""


def get_user_permissions(user: User) -> List[str]:
    """Get all permissions for a user based on their role"""
    permissions = set()

    # Staff users have all permissions
    if user.is_staff:
        return ["*"]

    # Get permissions from role
    if user.role:
        for perm in user.role.permissions:
            permissions.add(perm.name)

    return list(permissions)


def has_permission(user: User, permission: str) -> bool:
    """Check if user has a specific permission"""
    user_perms = get_user_permissions(user)

    # Admin has all permissions
    if "*" in user_perms:
        return True

    return permission in user_perms


def require_permission(permission: str):
    """Decorator to require a specific permission"""

    def dependency(current_user: User = Depends(get_current_user), db=Depends(get_db)):
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=403, detail=f"Permission denied: {permission} required"
            )
        return current_user

    return dependency


def require_permissions(permissions: List[str]):
    """Decorator to require multiple permissions (any of them)"""

    def dependency(current_user: User = Depends(get_current_user), db=Depends(get_db)):
        user_perms = get_user_permissions(current_user)

        if "*" in user_perms:
            return current_user

        if not any(p in user_perms for p in permissions):
            raise HTTPException(
                status_code=403,
                detail=f"One of these permissions required: {', '.join(permissions)}",
            )
        return current_user

    return dependency


def require_all_permissions(permissions: List[str]):
    """Decorator to require all permissions"""

    def dependency(current_user: User = Depends(get_current_user), db=Depends(get_db)):
        user_perms = get_user_permissions(current_user)

        if "*" in user_perms:
            return current_user

        missing = [p for p in permissions if p not in user_perms]
        if missing:
            raise HTTPException(
                status_code=403, detail=f"Missing permissions: {', '.join(missing)}"
            )
        return current_user

    return dependency


# Permission constants
class Permissions:
    # Product permissions
    VIEW_PRODUCTS = "view_products"
    CREATE_PRODUCTS = "create_products"
    EDIT_PRODUCTS = "edit_products"
    DELETE_PRODUCTS = "delete_products"

    # Order permissions
    VIEW_ORDERS = "view_orders"
    CREATE_ORDERS = "create_orders"
    EDIT_ORDERS = "edit_orders"
    DELETE_ORDERS = "delete_orders"

    # User permissions
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"

    # Inventory permissions
    VIEW_INVENTORY = "view_inventory"
    MANAGE_INVENTORY = "manage_inventory"
    VIEW_STOCK_ALERTS = "view_stock_alerts"
    MANAGE_SUPPLIERS = "manage_suppliers"

    # Reports/Dashboard
    VIEW_REPORTS = "view_reports"
    VIEW_ANALYTICS = "view_analytics"

    # RBAC management
    MANAGE_ROLES = "manage_roles"
    MANAGE_PERMISSIONS = "manage_permissions"

    # Categories
    VIEW_CATEGORIES = "view_categories"
    MANAGE_CATEGORIES = "manage_categories"
