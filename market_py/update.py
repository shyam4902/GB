import argparse
import json
import os
import sqlite3
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_HOST = os.getenv("GB_API_HOST", "https://api.gameblazers.com")
DEFAULT_DB = Path(__file__).with_name("gameblazers.db")


def fetch_sales_page(page, token, opener=urlopen, retries=3):
    params = {
        "Sport": "Nfl",
        "IsUserListings": "false",
        "SortCriteria": "DateSoldDesc",
        "IsSold": "true",
    }
    request = Request(
        f"{API_HOST}/api/v1/marketplace/getsales/page/{page}?{urlencode(params)}",
        headers={
        "Accept": "*/*",
            "Authorization": f"Bearer {token}",
            "Origin": "https://app.gameblazers.com",
            "Referer": "https://app.gameblazers.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/140 Safari/537.36",
        },
    )

    for attempt in range(retries):
        try:
            with opener(request, timeout=20) as response:
                data = json.load(response)
                if not isinstance(data, list):
                    raise RuntimeError(f"Unexpected marketplace response: {type(data).__name__}")
                return data
        except HTTPError as error:
            if error.code == 401:
                raise RuntimeError("GameBlazers login expired; provide a fresh GB_ACCESS_TOKEN.") from error
            if error.code != 429 and error.code < 500:
                raise
            if attempt + 1 == retries:
                raise
            delay = min(float(error.headers.get("Retry-After", 2 ** attempt)), 60)
            time.sleep(delay)
        except URLError:
            if attempt + 1 == retries:
                raise
            time.sleep(2 ** attempt)

    return []


def init_db(db_path=DEFAULT_DB):
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS marketplace_sales_v2 (
            listing_id TEXT PRIMARY KEY,
            listing_item_id TEXT,
            player_item_id TEXT,
            player_id TEXT,
            player_name TEXT,
            player_team TEXT,
            player_position TEXT,
            collection_name TEXT,
            multiplier REAL,
            salary INTEGER,
            overall_rating INTEGER,
            adjusted_overall INTEGER,
            is_franchise INTEGER,
            is_tradeable INTEGER,
            is_rookie INTEGER,
            price REAL,
            listing_type TEXT,
            card_expires_at TEXT,
            listing_created_at TEXT,
            sold_at TEXT,
            listing_updated_at TEXT,
            inserted_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


def _name(value):
    if isinstance(value, dict):
        return value.get("name") or value.get("abbreviation")
    return value


def normalize_sale(item):
    listing_item = item.get("marketplaceListingItemDetails") or {}
    player_item = listing_item.get("playerItemDetails") or {}
    player = player_item.get("playerDetails") or {}
    team = player.get("team") or {}
    collection = player_item.get("playerCollectionDetails") or {}

    return (
        item.get("id"),
        listing_item.get("id"),
        player_item.get("playerItemId"),
        player.get("playerId"),
        player.get("fullName"),
        team.get("abbreviation") or team.get("teamName"),
        ",".join(player.get("positions") or []).upper() or None,
        collection.get("name"),
        player_item.get("multiplier"),
        player_item.get("salary"),
        player_item.get("overallRating"),
        player_item.get("adjustedOverall"),
        int(bool(player_item.get("isFranchise"))),
        int(bool(player_item.get("isTradeable"))),
        int(bool(player_item.get("isRookie"))),
        item.get("price"),
        item.get("listingType"),
        player_item.get("expiringDate"),
        item.get("dateCreated"),
        item.get("dateSold"),
        item.get("lastUpdated"),
    )


def save_sales(conn, items):
    rows = [normalize_sale(item) for item in items if item.get("id")]
    before = conn.total_changes
    conn.executemany(
        """
        INSERT OR IGNORE INTO marketplace_sales_v2 (
            listing_id, listing_item_id, player_item_id, player_id,
            player_name, player_team, player_position, collection_name,
            multiplier, salary, overall_rating, adjusted_overall,
            is_franchise, is_tradeable, is_rookie, price, listing_type,
            card_expires_at, listing_created_at, sold_at, listing_updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    return conn.total_changes - before


def has_sale(conn, listing_id):
    return conn.execute(
        "SELECT 1 FROM marketplace_sales_v2 WHERE listing_id = ?", (listing_id,)
    ).fetchone() is not None


def update_sales(conn, token, max_pages=20, max_new=200, wait_seconds=4):
    total = 0
    for page in range(1, max_pages + 1):
        if page > 1:
            time.sleep(wait_seconds)

        items = fetch_sales_page(page, token)
        if not items:
            break

        new_items = []
        reached_existing = False
        for item in items:
            listing_id = item.get("id")
            if listing_id and has_sale(conn, listing_id):
                reached_existing = True
                break
            new_items.append(item)

        saved = save_sales(conn, new_items[: max_new - total])
        total += saved
        print(f"Page {page}: saved {saved} new sales ({total} total)")

        if reached_existing or total >= max_new:
            break

    return total


def self_test():
    sample = {
        "id": "listing-1",
        "price": 3,
        "listingType": "Listing",
        "dateSold": "2026-08-12T22:33:42Z",
        "marketplaceListingItemDetails": {
            "id": "detail-1",
            "playerItemDetails": {
                "playerItemId": "item-1",
                "multiplier": 1.2,
                "salary": 10800,
                "isTradeable": True,
                "playerDetails": {
                    "playerId": "player-1",
                    "fullName": "Puka Nacua",
                    "team": {"abbreviation": "LAR"},
                    "position": "WR",
                },
            },
        },
    }
    conn = init_db(":memory:")
    assert save_sales(conn, [sample, sample]) == 1
    assert has_sale(conn, "listing-1")
    assert conn.execute(
        "SELECT player_name, player_team, multiplier FROM marketplace_sales_v2"
    ).fetchone() == ("Puka Nacua", "LAR", 1.2)
    conn.close()
    print("Self-test passed")


def main():
    parser = argparse.ArgumentParser(description="Incrementally import GameBlazers NFL sales")
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--pages", type=int, default=20)
    parser.add_argument("--max-new", type=int, default=200)
    parser.add_argument("--wait", type=float, default=4)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    token = os.getenv("GB_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Set GB_ACCESS_TOKEN for your current GameBlazers session.")

    conn = init_db(args.db)
    try:
        total = update_sales(conn, token, args.pages, args.max_new, args.wait)
        print(f"Done: {total} new sales imported")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
