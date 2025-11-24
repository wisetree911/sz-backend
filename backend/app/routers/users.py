from fastapi import APIRouter, status
from app.schemas.user import UserCreate, UserResponse
from app.core.database import SessionDep
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(session: SessionDep, user_id: int):
    return await UserService.get_one(session=session, user_id=user_id)

@router.get("/", response_model=list[UserResponse])
async def get_users(session: SessionDep):
    return await UserService.get_all(session=session)

@router.post("/", response_model=UserResponse)
async def create_user(session: SessionDep, user_schema: UserCreate):
    return await UserService.create(session=session, user_schema=user_schema)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(session: SessionDep, user_id: int):
    await UserService.delete(session=session, user_id=user_id)
    return
    
