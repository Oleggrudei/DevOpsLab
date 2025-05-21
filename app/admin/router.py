from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.dependencies.auth_dep import get_current_admin_user
from app.dependencies.dao_dep import get_session_with_commit
from app.exceptions import UserNotFoundException
from app.auth.dao import UsersDAO, RoleDAO
from app.auth.schemas import SIdFilterModel, SUserInfo
from app.admin.schemas import SUserUpdateRole

router = APIRouter()


@router.get("/get_user/{user_id}")
async def get_user(session: AsyncSession = Depends(get_session_with_commit),
                   user_id: int = None, user_data: User = Depends(get_current_admin_user)
                   ) -> SUserInfo:
    find_user = await UsersDAO(session).find_one_or_none_by_id(data_id=user_id)
    if not find_user:
        raise UserNotFoundException

    return find_user


@router.get("/all_users/")
async def get_all_users(session: AsyncSession = Depends(get_session_with_commit),
                        user_data: User = Depends(get_current_admin_user)
                        ) -> List[SUserInfo]:
    return await UsersDAO(session).find_all()

@router.get("/all_role")
async def get_all_role(session: AsyncSession = Depends(get_session_with_commit),
                       user_data: User = Depends(get_current_admin_user)
                       ):
    return await RoleDAO(session).find_all()


@router.delete("/delete_user/{user_id}")
async def delete_user(session: AsyncSession = Depends(get_session_with_commit),
                      user_id: int = None, user_data: User = Depends(get_current_admin_user)
                      ):
    delete_users = await UsersDAO(session).delete(filters=SIdFilterModel(id=user_id))
    if not delete_users:
        raise UserNotFoundException

    return delete_users


@router.put("/change_role/{user_id}")
async def change_role(new_role_id: SUserUpdateRole, user_id: int = None,
                      session: AsyncSession = Depends(get_session_with_commit),
                      user_data: User = Depends(get_current_admin_user)
                      ):
    change_role = await UsersDAO(session).update(filters=SIdFilterModel(id=user_id),
                                                 values=new_role_id)
    if not change_role:
        raise UserNotFoundException

    return change_role
