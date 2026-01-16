"""
Basic MongoDB connection example.

This example demonstrates how to connect to MongoDB and perform
basic operations using gds_mongodb.
"""

from gds_mongodb import MongoDBConnection


def main():
    """Run basic MongoDB connection example."""
    # Create connection
    conn = MongoDBConnection(
        host="localhost",
        port=27017,
        database="example_db",
        username="admin",
        password="password",
    )

    try:
        # Connect to database
        print("Connecting to MongoDB...")
        conn.connect()
        print("Connected successfully!")

        # Get connection info
        info = conn.get_connection_info()
        print("\nConnection Info:")
        print(f"  Host: {info['host']}:{info['port']}")
        print(f"  Database: {info['database']}")
        print(f"  Connected: {info['connected']}")

        # Get collections
        print("\nCollections in database:")
        collections = conn.get_collection_names()
        for collection in collections:
            print(f"  - {collection}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Disconnect
        conn.disconnect()
        print("\nDisconnected from MongoDB")


if __name__ == "__main__":
    main()
