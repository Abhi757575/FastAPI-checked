from src.db.models import User
from src.db.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from .schemas import UserCreateModel
from .utils import generate_password_hash

class UserService:
    async def get_user(self, email, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)

        user = result.scalar_one_or_none()
        
        return user

    async def user_exists(self, email, session: AsyncSession):
        user = await self.get_user(email, session)
        
        return True if user is not None else False
            
    '''
    async def create_user(self, user_data, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        new_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
            email=user_data.email,
            password_hash=generate_password_hash(user_data.password),
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user
    '''
    async def create_user(self, user_data, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        password = user_data_dict.pop("password")

        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password_hash(password)
        new_user.role = "user"

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user
    

    