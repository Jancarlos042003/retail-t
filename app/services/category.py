from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = CategoryRepository(session)

    async def get_by_id(self, id: UUID) -> CategoryRead:
        category = await self.repo.get_by_id(id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
            )
        return CategoryRead.model_validate(category)

    async def get_all(self) -> list[CategoryRead]:
        categories = await self.repo.get_all()
        return [CategoryRead.model_validate(c) for c in categories]

    async def create(self, data: CategoryCreate) -> CategoryRead:
        category = await self.repo.create(data)
        return CategoryRead.model_validate(category)

    async def update(self, id: UUID, data: CategoryUpdate) -> CategoryRead:
        category = await self.repo.update(id, data)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
            )
        return CategoryRead.model_validate(category)

    async def delete(self, id: UUID) -> None:
        deleted = await self.repo.delete(id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
            )
