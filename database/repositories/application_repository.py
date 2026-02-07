"""
🚀 ULTRA-FAST User Repository
Optimized for maximum speed with minimal overhead
"""
from sqlalchemy import select, update, delete, exists, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any
import json

from database.models.user import User


class UserRepo:
    """
    High-performance User repository
    All methods are static for zero instantiation overhead
    """

    __slots__ = ()

    # ==================== CREATE ====================

    @staticmethod
    async def create(
            session: AsyncSession,
            user_id: int,
            first_name: str,
            last_name: Optional[str] = None,
            username: Optional[str] = None,
            language_code: str = "uz"
    ) -> User:
        """Create new user - returns created user"""
        user = User(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            language_code=language_code
        )
        session.add(user)
        await session.commit()
        return user

    @staticmethod
    async def get_or_create(
            session: AsyncSession,
            user_id: int,
            first_name: str,
            last_name: Optional[str] = None,
            username: Optional[str] = None,
            language_code: str = "uz"
    ) -> tuple[User, bool]:
        """Get existing user or create new one. Returns (user, created)"""
        user = await session.get(User, user_id)
        if user:
            return user, False

        user = User(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            language_code=language_code
        )
        session.add(user)
        await session.commit()
        return user, True

    # ==================== READ ====================

    @staticmethod
    async def get(session: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID - fastest possible lookup"""
        return await session.get(User, user_id)

    @staticmethod
    async def get_by_username(session: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def exists(session: AsyncSession, user_id: int) -> bool:
        """Check if user exists - ultra fast"""
        result = await session.execute(
            select(exists().where(User.id == user_id))
        )
        return result.scalar()

    @staticmethod
    async def get_id(session: AsyncSession, username: str) -> Optional[int]:
        """Get user ID by username"""
        result = await session.execute(
            select(User.id).where(User.username == username)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_username(session: AsyncSession, user_id: int) -> Optional[str]:
        """Get username by user ID"""
        result = await session.execute(
            select(User.username).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_first_name(session: AsyncSession, user_id: int) -> Optional[str]:
        """Get first name"""
        result = await session.execute(
            select(User.first_name).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_last_name(session: AsyncSession, user_id: int) -> Optional[str]:
        """Get last name"""
        result = await session.execute(
            select(User.last_name).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_full_name(session: AsyncSession, user_id: int) -> Optional[str]:
        """Get full name concatenated"""
        result = await session.execute(
            select(User.first_name, User.last_name).where(User.id == user_id)
        )
        row = result.one_or_none()
        if not row:
            return None
        first, last = row
        return f"{first} {last}" if last else first

    @staticmethod
    async def get_language(session: AsyncSession, user_id: int) -> Optional[str]:
        """Get user language code"""
        result = await session.execute(
            select(User.language_code).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def is_active(session: AsyncSession, user_id: int) -> bool:
        """Check if user is active"""
        result = await session.execute(
            select(User.is_active).where(User.id == user_id)
        )
        return result.scalar_one_or_none() or False

    @staticmethod
    async def is_blocked(session: AsyncSession, user_id: int) -> bool:
        """Check if user is blocked"""
        result = await session.execute(
            select(User.is_blocked).where(User.id == user_id)
        )
        return result.scalar_one_or_none() or False

    # ==================== STATE MANAGEMENT ====================

    @staticmethod
    async def get_state(session: AsyncSession, user_id: int) -> Optional[str]:
        """Get user state - ULTRA FAST"""
        result = await session.execute(
            select(User.state).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_state_data(session: AsyncSession, user_id: int) -> Optional[dict]:
        """Get user state data as dict"""
        result = await session.execute(
            select(User.state_data).where(User.id == user_id)
        )
        data = result.scalar_one_or_none()
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None
        return None

    @staticmethod
    async def get_state_with_data(session: AsyncSession, user_id: int) -> tuple[Optional[str], Optional[dict]]:
        """Get both state and state_data in single query"""
        result = await session.execute(
            select(User.state, User.state_data).where(User.id == user_id)
        )
        row = result.one_or_none()
        if not row:
            return None, None

        state, data = row
        parsed_data = None
        if data:
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError:
                pass
        return state, parsed_data

    @staticmethod
    async def set_state(
            session: AsyncSession,
            user_id: int,
            state: str,
            state_data: Optional[dict] = None
    ) -> bool:
        """Set user state and optional data - FAST"""
        data_str = json.dumps(state_data, ensure_ascii=False) if state_data else None
        result = await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(state=state, state_data=data_str)
        )
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def update_state_data(
            session: AsyncSession,
            user_id: int,
            **kwargs
    ) -> bool:
        """Update state data by merging with existing data"""
        current = await UserRepo.get_state_data(session, user_id)
        if current is None:
            current = {}
        current.update(kwargs)

        result = await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(state_data=json.dumps(current, ensure_ascii=False))
        )
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def clear_state(session: AsyncSession, user_id: int) -> bool:
        """Reset state to idle and clear data"""
        result = await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(state="idle", state_data=None)
        )
        await session.commit()
        return result.rowcount > 0

    # ==================== UPDATE ====================

    @staticmethod
    async def update(
            session: AsyncSession,
            user_id: int,
            **kwargs
    ) -> bool:
        """Update user fields - generic fast update"""
        if not kwargs:
            return False
        result = await session.execute(
            update(User).where(User.id == user_id).values(**kwargs)
        )
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def set_first_name(session: AsyncSession, user_id: int, first_name: str) -> bool:
        """Update first name"""
        result = await session.execute(
            update(User).where(User.id == user_id).values(first_name=first_name)
        )
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def set_last_name(session: AsyncSession, user_id: int, last_name: str) -> bool:
        """Update last name"""
        result = await session.execute(
            update(User).where(User.id == user_id).values(last_name=last_name)
        )
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def set_username(session: AsyncSession, user_id: int, username: Optional[str]) -> bool:
        """Update username"""
        result = await session.execute(
            update(User).where(User.id == user_id).values(username=username)
        )
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def set_language(session: AsyncSession, user_id: int, language_code: str) -> bool:
        """Update language"""
        result = await session.execute(
            update(User).where(User.id == user_id).values(language_code=language_code)
        )
        await session.commit()
        return result.rowcount > 0


    @staticmethod
    async def set_active(session: AsyncSession, user_id: int, is_active: bool) -> bool:
        """Set user active status"""
        result = await session.execute(
            update(User).where(User.id == user_id).values(is_active=is_active)
        )
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def set_blocked(session: AsyncSession, user_id: int, is_blocked: bool) -> bool:
        """Set user blocked status"""
        result = await session.execute(
            update(User).where(User.id == user_id).values(is_blocked=is_blocked)
        )
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def sync_telegram_data(
            session: AsyncSession,
            user_id: int,
            first_name: str,
            last_name: Optional[str] = None,
            username: Optional[str] = None,
            language_code: Optional[str] = None
    ) -> bool:
        """Sync user data from Telegram update"""
        values = {"first_name": first_name}
        if last_name is not None:
            values["last_name"] = last_name
        if username is not None:
            values["username"] = username
        if language_code is not None:
            values["language_code"] = language_code

        result = await session.execute(
            update(User).where(User.id == user_id).values(**values)
        )
        await session.commit()
        return result.rowcount > 0

    # ==================== DELETE ====================

    @staticmethod
    async def delete(session: AsyncSession, user_id: int) -> bool:
        """Delete user"""
        result = await session.execute(
            delete(User).where(User.id == user_id)
        )
        await session.commit()
        return result.rowcount > 0

    # ==================== BULK/LIST OPERATIONS ====================

    @staticmethod
    async def get_all_ids(session: AsyncSession, active_only: bool = True) -> list[int]:
        """Get all user IDs"""
        query = select(User.id)
        if active_only:
            query = query.where(User.is_active == True)
        result = await session.execute(query)
        return list(result.scalars().all())


    @staticmethod
    async def count(session: AsyncSession, active_only: bool = True) -> int:
        """Count users"""
        query = select(func.count(User.id))
        if active_only:
            query = query.where(User.is_active == True)
        result = await session.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def get_users_by_state(session: AsyncSession, state: str) -> list[User]:
        """Get all users in specific state"""
        result = await session.execute(
            select(User).where(User.state == state, User.is_active == True)
        )
        return list(result.scalars().all())