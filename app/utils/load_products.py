import httpx

from app.database.mongo import mongo
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

DUMMYJSON_BASE_URL = "https://dummyjson.com"


def _fetch_categories(client: httpx.Client) -> list[dict]:
    response = client.get(f"{DUMMYJSON_BASE_URL}/products/categories")
    response.raise_for_status()
    return response.json()


def _fetch_all_products(client: httpx.Client) -> list[dict]:
    response = client.get(f"{DUMMYJSON_BASE_URL}/products", params={"limit": 0})
    response.raise_for_status()
    return response.json()["products"]


def load_dummy_data():
    db = mongo.db

    # Clear existing data
    db.categories.delete_many({})
    db.products.delete_many({})

    with httpx.Client(timeout=30) as client:
        remote_categories = _fetch_categories(client)
        remote_products = _fetch_all_products(client)

    categories = [{"name": cat["name"], "slug": cat["slug"]} for cat in remote_categories]

    result = db.categories.insert_many(categories)
    cat_ids = {cat["slug"]: _id for cat, _id in zip(categories, result.inserted_ids)}
    logger.info(f"Created {len(cat_ids)} categories")

    products = [
        {
            "name": product["title"],
            "category_id": cat_ids[product["category"]],
            "price": round(product["price"] * 100),
            "stock": product["stock"],
            "description": product["description"],
        }
        for product in remote_products
        if product["category"] in cat_ids
    ]

    result = db.products.insert_many(products)
    logger.info(f"Created {len(result.inserted_ids)} products")

    return {"categories": len(cat_ids), "products": len(result.inserted_ids)}


def run() -> None:
    summary = load_dummy_data()
    logger.info(f"Seed complete: {summary}")
