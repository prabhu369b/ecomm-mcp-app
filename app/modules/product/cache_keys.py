class ProductCacheKeys:

    @staticmethod
    def version_key() -> str:
        return "products:version"

    @staticmethod
    def list_key(version: str, q: str | None, category_id: str | None, page: int, page_size: int) -> str:
        return f"products:list:{version}:{q or ''}:{category_id or ''}:{page}:{page_size}"