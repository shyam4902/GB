import os
import json
import requests
import sqlite3
import time
import random
from requests.exceptions import HTTPError

# Configuration
tRPC_ENDPOINT = os.getenv(
    "GB_API_HOST",
    "https://play.gameblazers.com/api/trpc/marketplace.queryMarketplaceWithCursor"
)

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

# Optional proxies via environment variables
PROXIES = {"http": os.getenv("HTTP_PROXY"), "https": os.getenv("HTTPS_PROXY")}
WAIT_SECONDS = 4  # polite wait between pages


def fetch_page(
    cursor=None,  # Can be None, int, float, or str
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
    next_cursor_for_payload will be None, int, float, or str.
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

    print(f"DEBUG: GET {tRPC_ENDPOINT}\nparams={params}\n")
    if isinstance(json_payload['cursor'], (int, float)):
        print(f"DEBUG EXTRA: Sending NUMERIC cursor in json_payload: {json_payload['cursor']} (type: {type(json_payload['cursor']).__name__})")
    elif json_payload['cursor'] is not None:
        print(f"DEBUG EXTRA: Sending STRING cursor in json_payload: '{json_payload['cursor']}'")
    else:
        print(f"DEBUG EXTRA: Sending NULL cursor in json_payload (initial page)")

    current_headers = HEADERS.copy()
    current_headers["User-Agent"] = random.choice(USER_AGENTS)
    active_proxies = {k: v for k, v in PROXIES.items() if v}

    try:
        resp = requests.get(tRPC_ENDPOINT, params=params, headers=current_headers, proxies=active_proxies or None, timeout=10)
        resp.raise_for_status()
    except HTTPError as e:
        print(f"HTTP {e.response.status_code} error for {resp.url}\nResponse: {e.response.text[:500]}\n") 
        return [], None
    except requests.exceptions.RequestException as e: 
        print(f"Request error: {e}\n")
        return [], None
    except Exception as e: 
        print(f"An unexpected error occurred in fetch_page: {e}\n")
        return [], None

    try:
        data = resp.json()
    except json.JSONDecodeError:
        print(f"DEBUG: Failed to decode JSON. Status: {resp.status_code}, Response: {resp.text[:500]}\n")
        return [], None
        
    if not isinstance(data, list) or not data:
        print(f"DEBUG: unexpected response format: {data}\n")
        return [], None
    
    entry = data[0]
    json_data_response = entry.get("result", {}).get("data", {}).get("json", {}) 
    if not json_data_response:
        print(f"DEBUG: 'json' field not found in response data structure: {entry}\n")
        return [], None

    listings = json_data_response.get("listings", [])
    raw_cursor_from_api = json_data_response.get("nextCursor")
    next_cursor_for_payload = None 

    if raw_cursor_from_api is not None:
        if isinstance(raw_cursor_from_api, (int, float)):
            next_cursor_for_payload = raw_cursor_from_api 
            print(f"DEBUG EXTRA: API returned NUMERIC nextCursor: {next_cursor_for_payload} (type: {type(next_cursor_for_payload).__name__})")
        else:
            try:
                next_cursor_for_payload = int(str(raw_cursor_from_api))
                print(f"DEBUG EXTRA: API returned STRING nextCursor '{raw_cursor_from_api}', converted to INT: {next_cursor_for_payload} (type: {type(next_cursor_for_payload).__name__})")
            except ValueError: 
                next_cursor_for_payload = str(raw_cursor_from_api) 
                print(f"DEBUG EXTRA: API returned non-numeric STRING nextCursor: '{next_cursor_for_payload}' (type: {type(next_cursor_for_payload).__name__})")
    else:
        print(f"DEBUG EXTRA: API returned no nextCursor (None).")
    
    return listings, next_cursor_for_payload


def init_db(db_path="gameblazers.db"):
    """Initializes the database and creates the sales_history table with the new schema."""
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
            
            -- New columns
            api_listing_id INTEGER,
            card_token_id INTEGER,
            player_api_id INTEGER,
            card_expires_at TEXT,
            card_rookie INTEGER, 
            player_team TEXT,
            player_position TEXT 
        )
        """
    ) # Renamed 'expiration_date' to 'listing_expires_at' for clarity
    conn.commit()
    return conn


def save_listings(conn, listings):
    """Saves a list of listings to the sales_history table, including new fields."""
    if not listings:
        return 0 
    cur = conn.cursor()
    rows_to_insert = []
    for item in listings:
        player_card_data = item.get("PlayerCard", {})
        player_relation_data = player_card_data.get("player_card_relation", {})

        # Existing fields
        name = player_relation_data.get("player_full_name", "")
        multiplier = item.get("multiplier") # Listing multiplier
        rarity = player_card_data.get("rarity")
        salary = player_card_data.get("PlayerSalary", {}).get("salary")
        listing_expires_at = item.get("expires") # This is the listing's expiration/sale time
        sale_price = item.get("price")

        # New fields
        api_listing_id = item.get("id")
        card_token_id = player_card_data.get("token_id") # Or item.get("token_id") if preferred
        player_api_id = player_card_data.get("player_id") # Or item.get("player_id")
        card_expires_at = player_card_data.get("expires") # Card's own expiration
        
        card_rookie_bool = player_card_data.get("rookie") # Boolean from JSON
        card_rookie_int = 1 if card_rookie_bool is True else 0 if card_rookie_bool is False else None # Convert to 1, 0 or None

        player_team = player_relation_data.get("team")
        player_position = player_relation_data.get("position")

        rows_to_insert.append((
            name, multiplier, rarity, salary, listing_expires_at, sale_price,
            api_listing_id, card_token_id, player_api_id, card_expires_at,
            card_rookie_int, player_team, player_position
        ))
    
    # Update the SQL INSERT statement to include new columns
    # Make sure the order of ? matches the order in the tuple above
    sql_insert = """
        INSERT INTO sales_history (
            player_name, multiplier, rarity, salary, listing_expires_at, sale_price,
            api_listing_id, card_token_id, player_api_id, card_expires_at,
            card_rookie, player_team, player_position
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur.executemany(sql_insert, rows_to_insert)
    conn.commit()
    return len(rows_to_insert) 


def run_basic_tests():
    print("Running basic fetch_page tests...")
    listings, cursor = fetch_page(limit=1)
    assert isinstance(listings, list), "fetch_page must return a list"
    assert len(listings) <= 1, "Limit=1 should return <=1 listing"
    assert cursor is None or isinstance(cursor, (str, int, float)), f"cursor must be None, str, int or float, got {type(cursor)}"
    print("  ✔ basic fetch_page passed")

    print("Running fetch_page test for SOLD items...")
    listings_sold, cursor_sold = fetch_page(limit=1, listing_type="SOLD")
    assert isinstance(listings_sold, list), "fetch_page (SOLD) must return a list"
    assert len(listings_sold) <= 1, "Limit=1 (SOLD) should return <=1 listing"
    assert cursor_sold is None or isinstance(cursor_sold, (str, int, float)), f"cursor (SOLD) must be None, str, int or float, got {type(cursor_sold)}"
    print("  ✔ basic fetch_page (SOLD) passed")


def main():
    run_basic_tests() 
    conn = init_db()

    print("\nStarting to fetch SOLD expiring items...")
    
    total_listings_fetched = 0 
    max_listings_to_fetch = 6000 

    current_listings, current_cursor = fetch_page( 
        limit=20, 
        order_by="updated-desc", price_lower=0, price_upper=200000,
        dynasty=False, distinct=False, listing_type="SOLD"
    )
    print(f"Fetched {len(current_listings)} sold expiring items, cursor for next page: {current_cursor} (type: {type(current_cursor).__name__})")
    
    if current_listings:
        num_saved = save_listings(conn, current_listings)
        total_listings_fetched += num_saved

    page_count_in_loop = 0 
    max_pages_to_fetch_in_loop = 299 

    while current_cursor is not None and \
          page_count_in_loop < max_pages_to_fetch_in_loop and \
          total_listings_fetched < max_listings_to_fetch:
              
        page_count_in_loop += 1
        actual_page_number = page_count_in_loop + 1 

        print(f"\n--- Fetching page {actual_page_number} (loop iteration {page_count_in_loop}) using cursor: {current_cursor} (type: {type(current_cursor).__name__}) ---")
        print(f"Total listings fetched so far: {total_listings_fetched} / {max_listings_to_fetch}")
        time.sleep(random.uniform(WAIT_SECONDS*0.5, WAIT_SECONDS*1.5))
        
        next_page_listings, next_page_cursor = fetch_page( 
            cursor=current_cursor, limit=20, order_by="updated-desc",
            price_lower=0, price_upper=200000, dynasty=False,
            distinct=False, listing_type="SOLD"
        )
        
        if not next_page_listings: 
            print(f"  ⚠️ No listings returned on page {actual_page_number} with cursor {current_cursor}. Stopping pagination.")
            break
        
        num_saved = save_listings(conn, next_page_listings)
        total_listings_fetched += num_saved
        print(f"  ✅ Saved {num_saved} more sold items from page {actual_page_number}, next cursor for payload: {next_page_cursor} (type: {type(next_page_cursor).__name__})")
        print(f"  Total listings now: {total_listings_fetched}")

        if current_cursor == next_page_cursor and next_page_listings: 
             print(f"  🛑 WARNING: Cursor did not change ('{next_page_cursor}') but listings were returned. Breaking to prevent infinite loop.")
             break
            
        current_cursor = next_page_cursor 

    if current_cursor is None:
        print(f"\nStopped: No next cursor provided by API. Fetched a total of {page_count_in_loop + 1} pages and {total_listings_fetched} listings.")
    elif page_count_in_loop >= max_pages_to_fetch_in_loop:
        print(f"\nStopped: Reached maximum page limit ({max_pages_to_fetch_in_loop + 1} pages). Fetched {total_listings_fetched} listings.")
    elif total_listings_fetched >= max_listings_to_fetch:
        print(f"\nStopped: Reached maximum listings limit ({max_listings_to_fetch} listings). Fetched across {page_count_in_loop + 1} pages.")
    
    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
