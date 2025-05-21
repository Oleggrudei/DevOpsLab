from typing import TypeVar, Generic, Type
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.logger import logger
from app.dao.database import Base

T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError("Модель має бути вказана в дочірньому класі")

    async def find_one_or_none_by_id(self, data_id: int):
        try:
            query = select(self.model).filter_by(id=data_id)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запис {self.model.__name__} з ID {data_id} {'знайдено' if record else 'не знайдено'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Помилка під час пошуку запису з ID {data_id}: {e}")
            raise

    async def find_one_or_none(self, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Пошук одного запису {self.model.__name__} за фільтрами: {filter_dict}")
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запис {'знайдено' if record else 'не знайдено'} за фільтрами: {filter_dict}"
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Помилка під час пошуку запису за фільтрами {filter_dict}: {e}")
            raise

    async def find_all(self, filters: BaseModel | None = None):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(f"Пошук усіх записів {self.model.__name__} за фільтрами: {filter_dict}")
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            records = result.scalars().all()
            logger.info(f"Знайдено {len(records)} записів.")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Помилка під час пошуку усіх записів за фільтрами {filter_dict}: {e}")
            raise

    async def add(self, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(f"Додавання запису {self.model.__name__} з параметрами: {values_dict}")
        try:
            new_instance = self.model(**values_dict)
            self._session.add(new_instance)
            logger.info(f"Запис {self.model.__name__} успішно додано.")
            await self._session.flush()
            return new_instance
        except SQLAlchemyError as e:
            logger.error(f"Помилка при додаванні запису: {e}")
            raise

    async def update(self, filters: BaseModel, values: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(
            f"Оновлення записів {self.model.__name__} за фільтром: {filter_dict} з параметрами: {values_dict}")
        try:
            query = (
                sqlalchemy_update(self.model)
                .where(*[getattr(self.model, k) == v for k, v in filter_dict.items()])
                .values(**values_dict)
                .execution_options(synchronize_session="fetch")
            )
            result = await self._session.execute(query)
            logger.info(f"Оновлено {result.rowcount} записів.")
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Помилка при оновленні записів: {e}")
            raise

    async def delete(self, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Видалення записів {self.model.__name__} за фільтром: {filter_dict}")
        if not filter_dict:
            logger.error("Потрібен принаймні один фільтр для видалення.")
            raise ValueError("Потрібен принаймні один фільтр для видалення.")
        try:
            query = sqlalchemy_delete(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            logger.info(f"Видалено {result.rowcount} записів.")
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Помилка при видаленні записів: {e}")
            raise
