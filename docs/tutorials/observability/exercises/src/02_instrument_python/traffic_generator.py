"""
Traffic Generator for Order Service

Generates realistic traffic patterns to demonstrate observability features.
"""

import time
import random
import requests
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("traffic-gen")

BASE_URL = "http://localhost:5000"
CUSTOMERS = ["cust_123", "cust_456", "cust_789", "vip_001"]
ITEMS = [
    {"name": "Widget", "price": 29.99},
    {"name": "Gadget", "price": 49.99},
    {"name": "Gizmo", "price": 9.99},
    {"name": "Thingamajig", "price": 19.99},
]


def create_order():
    """Simulate creating an order."""
    customer = random.choice(CUSTOMERS)
    # 10% chance of missing customer_id to trigger validation error
    if random.random() < 0.1:
        customer = ""

    items = random.sample(ITEMS, k=random.randint(1, 3))

    payload = {"customer_id": customer, "items": items}

    try:
        resp = requests.post(f"{BASE_URL}/api/orders", json=payload)
        if resp.status_code == 201:
            logger.info(f"Order created: {resp.json().get('order_id')}")
            return resp.json().get("order_id")
        else:
            logger.warning(f"Failed to create order: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return None


def get_order(order_id):
    """Simulate fetching an order."""
    if not order_id:
        return

    try:
        resp = requests.get(f"{BASE_URL}/api/orders/{order_id}")
        if resp.status_code == 200:
            logger.info(f"Order fetched: {order_id}")
        else:
            logger.warning(f"Failed to fetch order: {resp.status_code}")
    except Exception as e:
        logger.error(f"Connection error: {e}")


def run_scenario():
    """Run a single user scenario."""
    order_id = create_order()
    if order_id:
        time.sleep(random.uniform(0.5, 2.0))
        get_order(order_id)


def main():
    print("Starting traffic generator (Press Ctrl+C to stop)...")

    # Simulate 3 concurrent users
    with ThreadPoolExecutor(max_workers=3) as executor:
        try:
            while True:
                # Submit tasks
                _ = [executor.submit(run_scenario) for _ in range(3)]

                # Wait for a bit
                time.sleep(random.uniform(1.0, 3.0))

        except KeyboardInterrupt:
            print("\nStopping traffic generator...")


if __name__ == "__main__":
    main()
