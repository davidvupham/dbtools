"""
Advanced query example for MongoDB.

This example demonstrates advanced querying capabilities
including sorting, limiting, and complex filters.
"""

from gds_mongodb import MongoDBConnection
from pymongo import ASCENDING, DESCENDING


def main():
    """Run advanced query examples."""
    with MongoDBConnection(
        host="localhost",
        port=27017,
        database="example_db",
        username="admin",
        password="password",
    ) as conn:
        print("=== Advanced MongoDB Queries ===\n")

        # Insert sample data
        print("Inserting sample data...")
        products = [
            {"name": "Laptop", "price": 1200, "category": "Electronics", "stock": 15},
            {"name": "Mouse", "price": 25, "category": "Electronics", "stock": 100},
            {"name": "Keyboard", "price": 75, "category": "Electronics", "stock": 50},
            {"name": "Monitor", "price": 300, "category": "Electronics", "stock": 30},
            {"name": "Desk", "price": 250, "category": "Furniture", "stock": 10},
            {"name": "Chair", "price": 150, "category": "Furniture", "stock": 20},
            {"name": "Lamp", "price": 40, "category": "Furniture", "stock": 45},
        ]

        # Clear existing data
        conn.delete_many("products", {})
        conn.insert_many("products", products)
        print(f"Inserted {len(products)} products\n")

        # 1. Simple filter
        print("1. Products under $100:")
        cheap_products = conn.execute_query(
            "products",
            {"price": {"$lt": 100}},
        )
        for product in cheap_products:
            print(f"   - {product['name']}: ${product['price']}")

        # 2. Multiple conditions (AND)
        print("\n2. Electronics under $100:")
        electronics = conn.execute_query(
            "products",
            {"category": "Electronics", "price": {"$lt": 100}},
        )
        for product in electronics:
            print(f"   - {product['name']}: ${product['price']}")

        # 3. OR conditions
        print("\n3. Products that are either expensive ($500+) or low stock (<20):")
        filtered = conn.execute_query(
            "products",
            {"$or": [{"price": {"$gte": 500}}, {"stock": {"$lt": 20}}]},
        )
        for product in filtered:
            print(f"   - {product['name']}: ${product['price']} (stock: {product['stock']})")

        # 4. Sorting
        print("\n4. Products sorted by price (descending):")
        sorted_products = conn.execute_query(
            "products",
            {},
            sort=[("price", DESCENDING)],
        )
        for product in sorted_products:
            print(f"   - {product['name']}: ${product['price']}")

        # 5. Limiting results
        print("\n5. Top 3 most expensive products:")
        top_products = conn.execute_query(
            "products",
            {},
            sort=[("price", DESCENDING)],
            limit=3,
        )
        for product in top_products:
            print(f"   - {product['name']}: ${product['price']}")

        # 6. Pagination (skip and limit)
        print("\n6. Products page 2 (items 3-5):")
        page_2 = conn.execute_query(
            "products",
            {},
            sort=[("name", ASCENDING)],
            skip=2,
            limit=3,
        )
        for product in page_2:
            print(f"   - {product['name']}")

        # 7. Projection (select specific fields)
        print("\n7. Product names and prices only:")
        names_prices = conn.execute_query(
            "products",
            {},
            projection={"name": 1, "price": 1, "_id": 0},
            sort=[("name", ASCENDING)],
        )
        for product in names_prices:
            print(f"   - {product['name']}: ${product['price']}")

        # 8. Range queries
        print("\n8. Products priced between $50 and $300:")
        mid_range = conn.execute_query(
            "products",
            {"price": {"$gte": 50, "$lte": 300}},
            sort=[("price", ASCENDING)],
        )
        for product in mid_range:
            print(f"   - {product['name']}: ${product['price']}")

        # 9. Text matching (regex)
        print("\n9. Products with 'e' in the name:")
        matching = conn.execute_query(
            "products",
            {"name": {"$regex": "e", "$options": "i"}},  # Case-insensitive
            sort=[("name", ASCENDING)],
        )
        for product in matching:
            print(f"   - {product['name']}")

        # 10. Aggregation using update
        print("\n10. Apply 10% discount to all Electronics:")
        result = conn.update_many(
            "products",
            {"category": "Electronics"},
            {"$mul": {"price": 0.9}},  # Multiply price by 0.9
        )
        print(f"   Updated {result['modified_count']} products")

        # Verify discount
        electronics_after = conn.execute_query(
            "products",
            {"category": "Electronics"},
            sort=[("name", ASCENDING)],
        )
        print("   Electronics after discount:")
        for product in electronics_after:
            print(f"     - {product['name']}: ${product['price']:.2f}")

        print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
