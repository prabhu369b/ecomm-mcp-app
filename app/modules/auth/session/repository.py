from datetime import datetime, timezone
from app.database.redis import RedisService
from app.modules.auth.schemas import SessionData
from app.modules.auth.session.keys import SessionKeys
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

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

        logger.info("session created: session_id=%s user_id=%s", session.session_id, session.user_id)

    async def find_by_id(self, session_id: str) -> SessionData | None:

        session = await self.redis.get(
            SessionKeys.session(session_id)
        )

        if not session:
            return None

        return SessionData.model_validate_json(session)

    async def list_by_user(self, user_id: str) -> list[SessionData]:

        session_ids = await self.redis.client.smembers(
            SessionKeys.user_sessions(user_id)
        )

        if not session_ids:
            return []

        session_ids = [str(session_id) for session_id in session_ids]

        pipe = self.redis.pipeline()
        for session_id in session_ids:
            pipe.get(SessionKeys.session(session_id))

        raw_sessions = await pipe.execute()

        sessions = []
        stale_ids = []
        for session_id, raw in zip(session_ids, raw_sessions):
            if raw is None:
                stale_ids.append(session_id)
                continue
            sessions.append(SessionData.model_validate_json(raw))

        if stale_ids:
            await self.redis.client.srem(SessionKeys.user_sessions(user_id), *stale_ids)

        sessions.sort(key=lambda s: s.last_used_at, reverse=True)
        return sessions

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

        logger.info("session rotated: session_id=%s", session.session_id)

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

        logger.info("session revoked: session_id=%s user_id=%s", session.session_id, session.user_id)

    async def revoke_by_id(self, user_id: str, session_id: str) -> bool:

        session = await self.find_by_id(session_id)

        if session is None or session.user_id != user_id:
            return False

        await self.revoke(session)
        return True

    async def revoke_all(self, user_id: str, except_session_id: str | None = None) -> int:

        sessions = await self.list_by_user(user_id)

        revoked = 0
        for session in sessions:
            if session.session_id == except_session_id:
                continue
            await self.revoke(session)
            revoked += 1

        return revoked
