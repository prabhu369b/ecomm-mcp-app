from app.services.mongo import mongo
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

def load_dummy_data():
    db = mongo.db
    
    # Clear existing data
    db.categories.delete_many({})
    db.products.delete_many({})
    
    # Create categories
    categories = [
        {"name": "Electronics", "slug": "electronics"},
        {"name": "Clothing", "slug": "clothing"},
        {"name": "Books", "slug": "books"},
        {"name": "Home", "slug": "home"}
    ]
    
    result = db.categories.insert_many(categories)
    cat_ids = {cat["slug"]: _id for cat, _id in zip(categories, result.inserted_ids)}
    logger.info(f"Created {len(cat_ids)} categories")
    
    # Create products using category IDs
    products = [
        {
            "name": "Wireless Bluetooth Headphones",
            "category_id": cat_ids["electronics"],
            "price": 4999,
            "stock": 50,
            "description": "Premium noise-cancelling wireless headphones with 30-hour battery life"
        },
        {
            "name": "USB-C Charging Cable",
            "category_id": cat_ids["electronics"],
            "price": 899,
            "stock": 200,
            "description": "Fast charging USB-C cable, 2 meters, braided nylon"
        },
        {
            "name": "Cotton T-Shirt",
            "category_id": cat_ids["clothing"],
            "price": 1299,
            "stock": 100,
            "description": "100% organic cotton, available in multiple colors"
        },
        {
            "name": "Denim Jeans",
            "category_id": cat_ids["clothing"],
            "price": 2999,
            "stock": 75,
            "description": "Classic fit denim jeans, premium quality"
        },
        {
            "name": "Python Programming Guide",
            "category_id": cat_ids["books"],
            "price": 3499,
            "stock": 30,
            "description": "Comprehensive guide to Python programming for beginners and experts"
        },
        {
            "name": "Coffee Mug Set",
            "category_id": cat_ids["home"],
            "price": 1599,
            "stock": 150,
            "description": "Ceramic coffee mug set of 4, dishwasher safe"
        }
    ]
    
    result = db.products.insert_many(products)
    logger.info(f"Created {len(result.inserted_ids)} products")
    
    return {"categories": len(cat_ids), "products": len(result.inserted_ids)}