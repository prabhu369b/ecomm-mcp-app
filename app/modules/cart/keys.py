class CartKeys:
    @staticmethod
    def cart(user_id: str) -> str:
        return f"cart:{user_id}"