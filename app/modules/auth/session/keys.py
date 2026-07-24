class SessionKeys:

    @staticmethod
    def session(
        session_id: str,
    ) -> str:

        return f"session:{session_id}"


    @staticmethod
    def refresh_index(
        refresh_hash: str,
    ) -> str:

        return f"refresh_index:{refresh_hash}"


    @staticmethod
    def user_sessions(
        user_id: str,
    ) -> str:

        return f"user_sessions:{user_id}"