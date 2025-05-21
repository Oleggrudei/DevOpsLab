import asyncio
from sqlalchemy import select
from app.dao.database import async_session_maker
from app.auth.models import Role, User

async def seed():
    async with async_session_maker() as session:
        # Додаємо ролі якщо їх ще немає
        result = await session.execute(select(Role).filter_by(name="User"))
        user_role = result.scalar_one_or_none()
        if not user_role:
            user_role = Role(id=1, name="User")
            session.add(user_role)
            await session.commit()

        result = await session.execute(select(Role).filter_by(name="Admin"))
        admin_role = result.scalar_one_or_none()
        if not admin_role:
            admin_role = Role(id=2, name="Admin")
            session.add(admin_role)
            await session.commit()

        # Додаємо адміністратора якщо його ще немає
        result = await session.execute(select(User).filter_by(email="admin@mail.com"))
        admin_user = result.scalar_one_or_none()
        if not admin_user:
            admin_user = User(
                phone_number="+38000000000",
                first_name="Admin",
                last_name="Admin",
                email="admin@mail.com",
                password="$2b$12$6mRG54pzNmw3rbQ6Ny9pXuexaQzfPsPOdImHyc0c/QWQT2/Avx/PO",
                role_id=2
            )
            session.add(admin_user)
            await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())