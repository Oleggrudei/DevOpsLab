from typing import Annotated

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base


class Role(Base):
    name: Mapped[Annotated[str, mapped_column(unique=True, nullable=False)]]
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"


class User(Base):
    phone_number: Mapped[Annotated[str, mapped_column(unique=True, nullable=False)]]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[Annotated[str, mapped_column(unique=True, nullable=False)]]
    password: Mapped[str]
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), default=1)
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="joined")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"