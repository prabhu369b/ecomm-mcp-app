import httpx

from app.config.settings import get_settings
from app.database.mongo import mongo
from app.core.logger import Logger

logger = Logger.get_logger(__name__)


def _fetch_categories(client: httpx.Client, base_url: str) -> list[dict]:
    response = client.get(f"{base_url}/products/categories")
    response.raise_for_status()
    return response.json()


def _fetch_all_products(client: httpx.Client, base_url: str) -> list[dict]:
    response = client.get(f"{base_url}/products", params={"limit": 0})
    response.raise_for_status()
    return response.json()["products"]


def load_catalog_v2() -> dict:
    settings = get_settings()
    base_url = settings.catalog_source_url

    if not base_url:
        raise RuntimeError("catalog_source_url is not configured (set CATALOG_SOURCE_URL)")

    db = mongo.db

    # Own collections — never touches the v1 products/categories collections.
    db.categories_v2.delete_many({})
    db.products_v2.delete_many({})

    with httpx.Client(timeout=30) as client:
        remote_categories = _fetch_categories(client, base_url)
        remote_products = _fetch_all_products(client, base_url)

    categories = [{"name": cat["name"], "slug": cat["slug"]} for cat in remote_categories]

    result = db.categories_v2.insert_many(categories)
    cat_ids = {cat["slug"]: _id for cat, _id in zip(categories, result.inserted_ids)}
    logger.info("v2 seed: created %s categories", len(cat_ids))

    products = [
        {
            "name": p["title"],
            "category_id": cat_ids[p["category"]],
            "price": round(p["price"] * 100),
            "stock": p["stock"],
            "description": p["description"],
            "brand": p.get("brand"),
            "sku": p.get("sku"),
            "rating": p.get("rating"),
            "discount_percentage": p.get("discountPercentage"),
            "tags": p.get("tags", []),
            "thumbnail": p.get("thumbnail"),
            "images": p.get("images", []),
            "warranty_information": p.get("warrantyInformation"),
            "shipping_information": p.get("shippingInformation"),
            "return_policy": p.get("returnPolicy"),
            "minimum_order_quantity": p.get("minimumOrderQuantity"),
        }
        for p in remote_products
        if p["category"] in cat_ids
    ]

    result = db.products_v2.insert_many(products)
    logger.info("v2 seed: created %s products", len(result.inserted_ids))

    return {"categories": len(cat_ids), "products": len(result.inserted_ids)}


def run() -> None:
    summary = load_catalog_v2()
    logger.info("v2 seed complete: %s", summary)
