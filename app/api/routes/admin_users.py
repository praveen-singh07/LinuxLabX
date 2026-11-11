from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.schemas.admin_users import (
    AdminOverview,
    AdminUserItem,
    AdminUserList,
    AdminUserRoleWrite,
    AdminUserStatusWrite,
)
from app.services.admin_user_service import (
    count_active_admins,
    get_overview,
    list_users,
)
from app.services.admin_audit_service import record_admin_action

router = APIRouter(
    prefix="/admin",
    tags=["Admin - User Management"],
    dependencies=[Depends(require_admin)],
)


@router.get("/overview", response_model=AdminOverview)
def admin_overview(db: Session = Depends(get_db)):
    return get_overview(db)


@router.get("/users", response_model=AdminUserList)
def admin_list_users(
    search: str | None = Query(default=None, max_length=100),
    status_filter: Literal["all", "active", "suspended"] = "all",
    role_filter: Literal["all", "student", "admin"] = "all",
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return list_users(
        db,
        search=search,
        status_filter=status_filter,
        role_filter=role_filter,
        limit=limit,
        offset=offset,
    )


@router.patch("/users/{user_id}/status", response_model=AdminUserItem)
def admin_set_user_status(
    user_id: int,
    data: AdminUserStatusWrite,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_admin.id and not data.is_active:
        raise HTTPException(status_code=400, detail="You cannot suspend your own account")
    if user.role == "admin" and user.is_active and not data.is_active:
        if count_active_admins(db) <= 1:
            raise HTTPException(status_code=409, detail="The last active administrator cannot be suspended")
    previous_value = "active" if user.is_active else "suspended"
    new_value = "active" if data.is_active else "suspended"
    if previous_value == new_value:
        return user
    record_admin_action(
        db,
        actor_user_id=current_admin.id,
        actor_name=current_admin.name,
        target_user_id=user.id,
        target_name=user.name,
        action="account.status",
        previous_value=previous_value,
        new_value=new_value,
    )
    user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/role", response_model=AdminUserItem)
def admin_set_user_role(
    user_id: int,
    data: AdminUserRoleWrite,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_admin.id and data.role != "admin":
        raise HTTPException(status_code=400, detail="You cannot remove your own administrator role")
    if user.role == "admin" and user.is_active and data.role != "admin":
        if count_active_admins(db) <= 1:
            raise HTTPException(status_code=409, detail="The last active administrator cannot be demoted")
    previous_value = user.role
    if previous_value == data.role:
        return user
    record_admin_action(
        db,
        actor_user_id=current_admin.id,
        actor_name=current_admin.name,
        target_user_id=user.id,
        target_name=user.name,
        action="account.role",
        previous_value=previous_value,
        new_value=data.role,
    )
    user.role = data.role
    db.commit()
    db.refresh(user)
    return user
