import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, TIMESTAMP, Integer, inspect
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

from app.config import settings


engine = create_async_engine(url=settings.DB_URL, echo=True, pool_size=5, max_overflow=0)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    # updated_at: Mapped[datetime] = mapped_column(
    #     TIMESTAMP,
    #     server_default=func.now(),
    #     onupdate=func.now()
    # )

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

    def to_dict(self, exclude_none: bool = False):
        result = {}
        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)

            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)

            if not exclude_none or value is not None:
                result[column.key] = value

        return result
