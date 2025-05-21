import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from app.auth.models import Role, User
from app.auth.dao import RoleDAO
from tests.schemas import RoleCreate

# Test data
test_user_data = {
    "email": "test@example.com",
    "phone_number": "+123456789",
    "first_name": "Test",
    "last_name": "User",
    "password": "password123",
    "confirm_password": "password123"
}

@pytest.fixture(autouse=True)
async def clean_roles(db_session: AsyncSession):
    await db_session.execute(delete(Role))
    await db_session.commit()

@pytest.fixture
async def default_role(db_session: AsyncSession):
    role_dao = RoleDAO(db_session)
    existing = await db_session.execute(
        select(Role).where(Role.name == "user")
    )
    role = existing.scalars().first()
    if not role:
        role = await role_dao.add(values=RoleCreate(name="user"))
        await db_session.commit()
    return role


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, default_role):
    # Test user registration
    response = await client.post("/auth/register/", json=test_user_data)
    
    assert response.status_code == 200
    assert response.json() == {"message": "Реєстрація успішна"}
    
    # Verify user was created in the database
    response = await client.post("/auth/login/", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_register_duplicate_user(client: AsyncClient, default_role):
    # Register a user
    await client.post("/auth/register/", json=test_user_data)
    
    # Try to register the same user again
    response = await client.post("/auth/register/", json=test_user_data)
    
    assert response.status_code == 409
    assert "already exists" in response.json().get("detail", "")

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, default_role):
    # Register a user first
    await client.post("/auth/register/", json=test_user_data)
    
    # Test login
    response = await client.post("/auth/login/", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "message": "Авторизація успішна!"
    }
    
    # Check that cookies are set
    assert "user_access_token" in response.cookies
    assert "user_refresh_token" in response.cookies

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, default_role):
    # Register a user first
    await client.post("/auth/register/", json=test_user_data)
    
    # Test login with wrong password
    response = await client.post("/auth/login/", json={
        "email": test_user_data["email"],
        "password": "wrong_password"
    })
    
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json().get("detail", "")

@pytest.mark.asyncio
async def test_logout(client: AsyncClient, default_role):
    # Register and login a user first
    await client.post("/auth/register/", json=test_user_data)
    login_response = await client.post("/auth/login/", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    # Get cookies from login response
    cookies = login_response.cookies
    
    # Test logout
    response = await client.post("/auth/logout", cookies=cookies)
    
    assert response.status_code == 200
    assert response.json() == {"message": "Користувач вийшов з системи"}
    
    # Check that cookies are cleared
    for cookie in ["user_access_token", "user_refresh_token"]:
        if cookie in response.cookies:
            assert response.cookies[cookie] == ""