import os
import json
import requests
import sqlite3
import time
import random
from requests.exceptions import HTTPError

# Configuration
tRPC_ENDPOINT = "https://play.gameblazers.com/api/trpc/marketplace.queryMarketplaceWithCursor"

# Standard headers to mimic browser
HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://app.gameblazers.com",
    "Referer": "https://app.gameblazers.com/"
}

# Rotate User-Agent to reduce fingerprinting
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5721.133 Safari/537.36"
]

WAIT_SECONDS = 3


def fetch_page(
    cursor=None,
    limit=20,
    order_by="price-asc",
    price_lower=0,
    price_upper=1000000,
    dynasty=False,
    distinct=False,
    listing_type=None
):
    """
    Fetch a page via tRPC GET (batch=1&input=<JSON>) as the browser does.
    Returns (listings, next_cursor_for_payload). On error, returns ([], None).
    """
    json_payload = {
        "position": None, "team": None, "multiplier": None, "playerName": "",
        "rarity": None, "take": limit, "orderBy": order_by,
        "priceLowerBound": price_lower, "priceUpperBound": price_upper,
        "dynasty": dynasty, "distinct": distinct, "cursor": cursor
    }
    if listing_type:
        json_payload["type"] = listing_type

    meta_values_content = {
        "position": ["undefined"], "team": ["undefined"],
        "multiplier": ["undefined"], "rarity": ["undefined"]
    }
    if cursor is None: 
        meta_values_content["cursor"] = ["undefined"]

    batch_input = {"0": {"json": json_payload, "meta": {"values": meta_values_content}}}
    params = {"batch": "1", "input": json.dumps(batch_input, separators=(",",":"))}

    print(f"Fetching from API with cursor: {cursor}")

    current_headers = HEADERS.copy()
    current_headers["User-Agent"] = random.choice(USER_AGENTS)

    try:
        resp = requests.get(tRPC_ENDPOINT, params=params, headers=current_headers, timeout=10)
        resp.raise_for_status()
    except HTTPError as e:
        print(f"❌ HTTP {e.response.status_code} error")
        print(f"Response: {e.response.text[:500]}")
        return [], None
    except requests.exceptions.RequestException as e: 
        print(f"❌ Request error: {e}")
        return [], None
    except Exception as e: 
        print(f"❌ Unexpected error: {e}")
        return [], None

    try:
        data = resp.json()
    except json.JSONDecodeError:
        print(f"❌ Failed to decode JSON. Status: {resp.status_code}")
        return [], None
        
    if not isinstance(data, list) or not data:
        print(f"❌ Unexpected response format")
        return [], None
    
    entry = data[0]
    json_data_response = entry.get("result", {}).get("data", {}).get("json", {}) 
    if not json_data_response:
        print(f"❌ 'json' field not found in response")
        return [], None

    listings = json_data_response.get("listings", [])
    raw_cursor_from_api = json_data_response.get("nextCursor")
    next_cursor_for_payload = None 

    if raw_cursor_from_api is not None:
        if isinstance(raw_cursor_from_api, (int, float)):
            next_cursor_for_payload = raw_cursor_from_api 
        else:
            try:
                next_cursor_for_payload = int(str(raw_cursor_from_api))
            except ValueError: 
                next_cursor_for_payload = str(raw_cursor_from_api)
    
    return listings, next_cursor_for_payload


def init_db(db_path="test_gameblazers.db"):
    """Initializes the test database"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sales_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            multiplier REAL,
            rarity TEXT,
            salary INTEGER,
            listing_expires_at TEXT, 
            sale_price REAL,
            inserted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            api_listing_id INTEGER UNIQUE, 
            card_token_id INTEGER,
            player_api_id INTEGER,
            card_expires_at TEXT,
            card_rookie INTEGER, 
            player_team TEXT,
            player_position TEXT 
        )
        """
    ) 
    conn.commit()
    return conn


def save_listings(conn, listings):
    """Saves listings to the database"""
    if not listings:
        return 0 
    cur = conn.cursor()
    rows_to_insert = []
    for item in listings:
        player_card_data = item.get("PlayerCard", {})
        player_relation_data = player_card_data.get("player_card_relation", {})

        name = player_relation_data.get("player_full_name", "")
        multiplier = item.get("multiplier") 
        rarity = player_card_data.get("rarity")
        salary = player_card_data.get("PlayerSalary", {}).get("salary")
        listing_expires_at = item.get("expires") 
        sale_price = item.get("price")
        api_listing_id = item.get("id")
        card_token_id = player_card_data.get("token_id") 
        player_api_id = player_card_data.get("player_id") 
        card_expires_at = player_card_data.get("expires") 
        
        card_rookie_bool = player_card_data.get("rookie") 
        card_rookie_int = 1 if card_rookie_bool is True else 0 if card_rookie_bool is False else None 

        player_team = player_relation_data.get("team")
        player_position = player_relation_data.get("position")

        rows_to_insert.append((
            name, multiplier, rarity, salary, listing_expires_at, sale_price,
            api_listing_id, card_token_id, player_api_id, card_expires_at,
            card_rookie_int, player_team, player_position
        ))
    
    sql_insert = """
        INSERT INTO sales_history (
            player_name, multiplier, rarity, salary, listing_expires_at, sale_price,
            api_listing_id, card_token_id, player_api_id, card_expires_at,
            card_rookie, player_team, player_position
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cur.executemany(sql_insert, rows_to_insert)
        conn.commit()
        return len(rows_to_insert) 
    except sqlite3.IntegrityError as e:
        print(f"⚠️ SQLite IntegrityError: {e}")
        conn.rollback() 
        return 0


def main():
    print("=" * 60)
    print("🧪 TEST RUN - Using separate test database")
    print("=" * 60)
    print()
    
    conn = init_db("test_gameblazers.db")
    print("✅ Created test database: test_gameblazers.db")
    print()

    print("🔍 Testing API connection with 1 page of SOLD listings...")
    print()
    
    page_listings, next_cursor = fetch_page( 
        cursor=None, 
        limit=20, 
        order_by="updated-desc",
        price_lower=0, 
        price_upper=200000,
        dynasty=False, 
        distinct=False, 
        listing_type="SOLD"
    )
    
    if not page_listings:
        print()
        print("❌ Failed to fetch data from API")
        print("The API might have changed or there might be connection issues.")
        conn.close()
        return
    
    print()
    print(f"✅ Successfully fetched {len(page_listings)} sold listings!")
    print(f"Next cursor available: {next_cursor is not None}")
    print()
    
    # Save to test database
    num_saved = save_listings(conn, page_listings)
    print(f"✅ Saved {num_saved} listings to test database")
    print()
    
    # Show sample data
    cur = conn.cursor()
    cur.execute("""
        SELECT player_name, player_team, player_position, sale_price, 
               listing_expires_at, rarity, multiplier
        FROM sales_history 
        ORDER BY listing_expires_at DESC 
        LIMIT 5
    """)
    
    print("📊 Sample of fetched data (5 most recent):")
    print("-" * 60)
    for row in cur.fetchall():
        name, team, pos, price, expires, rarity, mult = row
        print(f"  {name} ({team} - {pos})")
        print(f"    Price: ${price}, Multiplier: {mult}x, Rarity: {rarity}")
        print(f"    Sold at: {expires}")
        print()
    
    conn.close()
    
    print("=" * 60)
    print("✅ TEST COMPLETE!")
    print("=" * 60)
    print()
    print("The API is working! Your original gameblazers.db was NOT touched.")
    print(f"Test data saved to: test_gameblazers.db")
    print()
    print("Next steps:")
    print("  1. Review the sample data above")
    print("  2. If it looks good, we can run the full update on your real database")


if __name__ == "__main__":
    main()
