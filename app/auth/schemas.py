import re
from typing import Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator, computed_field

from app.auth.utils import get_password_hash


class EmailModel(BaseModel):
    email: EmailStr = Field(description="Email")
    model_config = ConfigDict(from_attributes=True)


class UserBase(EmailModel):
    phone_number: str = Field(description="Phone number in international format starting with '+'")
    first_name: str = Field(min_length=3, max_length=50, description="First name, 3 to 50 characters")
    last_name: str = Field(min_length=3, max_length=50, description="Last name, 3 to 50 characters")

    @field_validator("phone_number")
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r'^\+\d{5,15}$', value):
            raise ValueError('Phone number must start with "+" and contain between 5 to 15 digits')
        return value


class SUserRegister(UserBase):
    password: str = Field(min_length=5, max_length=50, description="Password, 5 to 50 characters")
    confirm_password: str = Field(min_length=5, max_length=50, description="Confirm password")

    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        self.password = get_password_hash(self.password)
        return self


class SUserAddDB(UserBase):
    password: str = Field(min_length=5, description="Password in HASH-string format")


class SUserAuth(EmailModel):
    password: str = Field(min_length=5, max_length=50, description="Password, 5 to 50 characters")


class RoleModel(BaseModel):
    id: int = Field(description="Role ID")
    name: str = Field(description="Role name")
    model_config = ConfigDict(from_attributes=True)


class SUserInfo(UserBase):
    id: int = Field(description="User ID")
    role: RoleModel = Field(exclude=True)

    @computed_field
    def role_name(self) -> str:
        return self.role.name

    @computed_field
    def role_id(self) -> int:
        return self.role.id


class SIdFilterModel(BaseModel):
    id: int | None = None


class SUserUpdateData(UserBase):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None

    @field_validator("phone_number")
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r'^\+\d{5,15}$', value):
            raise ValueError('Phone number must start with "+" and contain between 5 to 15 digits')
        return value


class SUserUpdatePassword(BaseModel):
    old_password: str = Field(min_length=5, max_length=50, description="Old password")
    password: str = Field(min_length=5, max_length=50, description="New password, 5 to 50 characters")
    confirm_password: str = Field(min_length=5, max_length=50, description="Confirm new password")

    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.old_password == self.password:
            raise ValueError("New password cannot be the same as the old password")
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        self.password = get_password_hash(self.password)
        return self

class SUserAddNewPassword(BaseModel):
    password: str = Field(min_length=5, description="Password in HASH-string format")

class SAddRole(BaseModel):
    name: str
    id: int