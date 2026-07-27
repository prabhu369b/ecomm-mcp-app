from datetime import datetime, timezone
from app.database.redis import RedisService
from app.modules.auth.schemas import SessionData
from app.modules.auth.session.keys import SessionKeys

class SessionRepository:

    SESSION_TTL = 60 * 60 * 24 * 30  # 30 days

    def __init__(self, redis: RedisService):
        self.redis = redis

    async def create(self, session: SessionData):
        session_key = SessionKeys.session(
            session.session_id
        )

        refresh_key = SessionKeys.refresh_index(
            session.refresh_hash
        )

        user_key = SessionKeys.user_sessions(
            session.user_id
        )

        pipe = self.redis.pipeline()

        pipe.setex(
            session_key,
            self.SESSION_TTL,
            session.model_dump_json()
        )

        pipe.setex(
            refresh_key,
            self.SESSION_TTL,
            session.session_id
        )

        pipe.sadd(
            user_key,
            session.session_id
        )

        await pipe.execute()

    async def find_by_refresh_hash(
        self,
        refresh_hash: str
    ) -> SessionData | None:

        session_id = await self.redis.get(
            SessionKeys.refresh_index(refresh_hash)
        )

        if not session_id:
            return None

        session = await self.redis.get(
            SessionKeys.session(str(session_id))
        )

        if not session:
            return None

        return SessionData.model_validate_json(session)

    async def rotate(
        self,
        session: SessionData,
        old_hash: str,
        new_hash: str,
    ) -> SessionData:

        updated = session.model_copy(update={
            "refresh_hash": new_hash,
            "last_used_at": datetime.now(timezone.utc).isoformat(),
        })

        pipe = self.redis.pipeline()

        pipe.delete(
            SessionKeys.refresh_index(old_hash)
        )

        pipe.setex(
            SessionKeys.refresh_index(new_hash),
            self.SESSION_TTL,
            session.session_id
        )

        pipe.setex(
            SessionKeys.session(session.session_id),
            self.SESSION_TTL,
            updated.model_dump_json()
        )

        await pipe.execute()

        return updated

    async def revoke(self, session: SessionData):

        pipe = self.redis.pipeline()

        pipe.delete(
            SessionKeys.refresh_index(session.refresh_hash)
        )

        pipe.delete(
            SessionKeys.session(session.session_id)
        )

        pipe.srem(
            SessionKeys.user_sessions(session.user_id),
            session.session_id
        )

        await pipe.execute()
