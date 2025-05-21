from fastapi import APIRouter, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.utils import authenticate_user, set_tokens
from app.dependencies.auth_dep import get_current_user, check_refresh_token
from app.dependencies.dao_dep import get_session_with_commit, get_session_without_commit
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException, UserNotFoundException
from app.auth.dao import UsersDAO, RoleDAO
from app.auth.schemas import SUserRegister, SUserAuth, EmailModel, SUserAddDB, SUserInfo, SIdFilterModel, \
    SUserUpdateData, SUserUpdatePassword, SUserAddNewPassword, SAddRole

router = APIRouter()


@router.post("/register/")
async def register_user(user_data: SUserRegister,
                        session: AsyncSession = Depends(get_session_with_commit)) -> dict:
    user_dao = UsersDAO(session)

    existing_user = await user_dao.find_one_or_none(filters=EmailModel(email=user_data.email))
    if existing_user:
        raise UserAlreadyExistsException

    user_data_dict = user_data.model_dump()
    user_data_dict.pop('confirm_password', None)

    await user_dao.add(values=SUserAddDB(**user_data_dict))
    return {'message': 'Реєстрація успішна'}


@router.post("/login/")
async def auth_user(
        response: Response,
        user_data: SUserAuth,
        session: AsyncSession = Depends(get_session_without_commit)
) -> dict:
    users_dao = UsersDAO(session)
    user = await users_dao.find_one_or_none(
        filters=EmailModel(email=user_data.email)
    )

    if not (user and await authenticate_user(user=user, password=user_data.password)):
        raise IncorrectEmailOrPasswordException
    set_tokens(response, user.id)
    return {
        'ok': True,
        'message': 'Авторизація успішна!'
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("user_access_token")
    response.delete_cookie("user_refresh_token")
    return {'message': 'Користувач вийшов з системи'}


@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)) -> SUserInfo:
    return SUserInfo.model_validate(user_data)


@router.delete("/me/delete/")
async def delete_user(user_data: User = Depends(get_current_user),
                      session: AsyncSession = Depends(get_session_with_commit)):
    user_delete = await UsersDAO(session).delete(filters=SIdFilterModel(id=user_data.id))

    if not user_delete:
        raise UserNotFoundException

    return {"message": "Акаунт видалено"}


@router.put("/me/update/")
async def update_user(user_data_update: SUserUpdateData,
                      user_data: User = Depends(get_current_user),
                      session: AsyncSession = Depends(get_session_with_commit)):
    user_update = await UsersDAO(session).update(filters=SIdFilterModel(id=user_data.id),
                                                 values=user_data_update)

    if not user_update:
        raise UserNotFoundException

    return {"message": "Дані користувача успішно оновлено"}


@router.put("/me/change_password/")
async def change_password(user_data_update: SUserUpdatePassword,
                          user_data: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session_with_commit)):
    user_update = user_data_update.model_dump()
    user_update.pop('old_password', None)
    user_update.pop('confirm_password', None)

    user_update = await UsersDAO(session).update(filters=SIdFilterModel(id=user_data.id),
                                                 values=SUserAddNewPassword(**user_update))

    if not user_update:
        raise UserNotFoundException

    return {"message": "Дані користувача успішно оновлено"}


@router.post("/refresh")
async def process_refresh_token(
        response: Response,
        user: User = Depends(check_refresh_token)
):
    set_tokens(response, user.id)
    return {"message": "Токени обновлені"}


@router.post("/add_role")
async def add_roles(add_role: SAddRole, session: AsyncSession = Depends(get_session_with_commit)):
    await RoleDAO(session).add(values=SAddRole(name=add_role.name, id=add_role.id))
