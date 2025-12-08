"""
CRUD operations example for MongoDB.

This example demonstrates Create, Read, Update, Delete operations
using gds_mongodb.
"""

from gds_mongodb import MongoDBConnection


def main():
    """Run CRUD operations example."""
    # Use context manager for automatic connection management
    with MongoDBConnection(
        host="localhost",
        port=27017,
        database="example_db",
        username="admin",
        password="password",
    ) as conn:
        print("=== MongoDB CRUD Operations Example ===\n")

        # CREATE - Insert documents
        print("1. INSERT Operations:")

        # Insert single document
        user1 = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30,
            "city": "New York",
        }
        result = conn.insert_one("users", user1)
        print(f"   Inserted user with ID: {result['inserted_id']}")

        # Insert multiple documents
        users = [
            {"name": "Jane Smith", "email": "jane@example.com", "age": 25},
            {"name": "Bob Johnson", "email": "bob@example.com", "age": 35},
            {"name": "Alice Williams", "email": "alice@example.com", "age": 28},
        ]
        result = conn.insert_many("users", users)
        print(f"   Inserted {len(result['inserted_ids'])} users")

        # READ - Query documents
        print("\n2. QUERY Operations:")

        # Find all users
        all_users = conn.execute_query("users", {})
        print(f"   Total users: {len(all_users)}")

        # Find users with filter
        young_users = conn.execute_query("users", {"age": {"$lt": 30}})
        print(f"   Users under 30: {len(young_users)}")
        for user in young_users:
            print(f"     - {user['name']}, age {user['age']}")

        # Find with projection (select specific fields)
        names_only = conn.execute_query("users", {}, projection={"name": 1, "email": 1, "_id": 0})
        print("\n   Users (names and emails only):")
        for user in names_only:
            print(f"     - {user['name']}: {user['email']}")

        # UPDATE - Modify documents
        print("\n3. UPDATE Operations:")

        # Update single document
        result = conn.update_one(
            "users",
            {"name": "John Doe"},
            {"$set": {"age": 31, "status": "updated"}},
        )
        print(f"   Updated {result['modified_count']} user (matched: {result['matched_count']})")

        # Update multiple documents
        result = conn.update_many(
            "users",
            {"age": {"$lt": 30}},
            {"$set": {"category": "young"}},
        )
        print(f"   Updated {result['modified_count']} users (matched: {result['matched_count']})")

        # Upsert (update or insert)
        result = conn.update_one(
            "users",
            {"email": "new@example.com"},
            {"$set": {"name": "New User", "age": 22}},
            upsert=True,
        )
        print(f"   Upserted document with ID: {result['upserted_id']}")

        # DELETE - Remove documents
        print("\n4. DELETE Operations:")

        # Delete single document
        result = conn.delete_one("users", {"email": "new@example.com"})
        print(f"   Deleted {result['deleted_count']} document")

        # Delete multiple documents
        result = conn.delete_many("users", {"age": {"$gte": 35}})
        print(f"   Deleted {result['deleted_count']} documents")

        # METADATA - Get information
        print("\n5. METADATA Operations:")

        # Get collection info
        field_info = conn.get_column_info("users", sample_size=10)
        print("   Fields in 'users' collection:")
        for field in field_info:
            print(f"     - {field['field_name']}: {field['data_type']} (appears in {field['count']} documents)")

        print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
