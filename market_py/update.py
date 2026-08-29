import argparse
import fcntl
import json
import os
import sqlite3
import sys
import time
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_HOST = os.getenv("GB_API_HOST", "https://api.gameblazers.com")
DEFAULT_DB = Path(__file__).with_name("gameblazers.db")


class SalesFetchError(RuntimeError):
    pass


def _retry_after_seconds(value):
    if not value:
        return 0
    try:
        return max(0, float(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(0, (retry_at - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return 0


def fetch_sales_page(page, token, opener=urlopen, sleeper=time.sleep):
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

    try:
        with opener(request, timeout=20) as response:
            data = json.load(response)
    except HTTPError as error:
        if error.code == 401:
            message = "fresh login token required"
        elif error.code == 403:
            message = "access forbidden"
        elif error.code == 429:
            retry_after = _retry_after_seconds(
                (getattr(error, "headers", None) or {}).get("Retry-After")
            )
            if retry_after:
                sleeper(retry_after)
            message = "rate limited"
        elif error.code >= 500:
            message = f"server error HTTP {error.code}"
        else:
            message = f"HTTP {error.code}"
        if error.fp is not None:
            error.close()
        raise SalesFetchError(
            f"Page {page} failed: {message}; checkpoint unchanged."
        ) from None
    except (URLError, TimeoutError, OSError) as error:
        raise SalesFetchError(
            f"Page {page} failed: network error; checkpoint unchanged."
        ) from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise SalesFetchError(
            f"Page {page} returned malformed JSON; checkpoint unchanged."
        ) from error

    if not isinstance(data, list):
        raise SalesFetchError(
            f"Page {page} returned unexpected {type(data).__name__}; checkpoint unchanged."
        )
    if any(not isinstance(item, dict) or not item.get("id") for item in data):
        raise SalesFetchError(
            f"Page {page} returned unexpected list contents; checkpoint unchanged."
        )
    return data


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
    with conn:
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
    return conn.total_changes - before


def has_sale(conn, listing_id):
    return conn.execute(
        "SELECT 1 FROM marketplace_sales_v2 WHERE listing_id = ?", (listing_id,)
    ).fetchone() is not None


def read_checkpoint(checkpoint_path, default=1):
    path = Path(checkpoint_path)
    if not path.exists():
        return default
    next_page = json.loads(path.read_text())["next_page"]
    if not isinstance(next_page, int) or next_page < 1:
        raise ValueError(f"Invalid checkpoint in {path}")
    return next_page


def set_checkpoint(checkpoint_path, next_page):
    if next_page < 1:
        raise ValueError("Checkpoint page must be at least 1")
    path = Path(checkpoint_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w") as handle:
        json.dump({"next_page": next_page}, handle)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def backfill_sales(
    conn,
    token,
    checkpoint_path,
    start_page=None,
    page_limit=1,
    fetcher=fetch_sales_page,
):
    if page_limit < 1:
        raise ValueError("Backfill page limit must be at least 1")
    page = start_page if start_page is not None else read_checkpoint(checkpoint_path)
    if page < 1:
        raise ValueError("Starting page must be at least 1")

    result = {
        "requested_pages": [],
        "rows_returned": 0,
        "inserted": 0,
        "duplicates": 0,
    }
    for _ in range(page_limit):
        items = fetcher(page, token)
        try:
            inserted = save_sales(conn, items)
        except (AttributeError, TypeError):
            raise SalesFetchError(
                f"Page {page} returned unexpected list contents; checkpoint unchanged."
            ) from None
        set_checkpoint(checkpoint_path, page + 1)
        result["requested_pages"].append(page)
        result["rows_returned"] += len(items)
        result["inserted"] += inserted
        result["duplicates"] += len(items) - inserted
        page += 1
    result["next_page"] = page
    return result


def check_integrity(db_path):
    path = Path(db_path).resolve()
    with closing(sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)) as conn:
        rows = [row[0] for row in conn.execute("PRAGMA integrity_check")]
    if rows != ["ok"]:
        raise sqlite3.DatabaseError("SQLite integrity check failed: " + "; ".join(rows))
    return "ok"


def backup_database(db_path, backup_dir=None, label=None):
    source_path = Path(db_path).resolve()
    backup_dir = Path(backup_dir or source_path.parent / "backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    name = source_path.stem + (f"-{label}" if label else "")
    backup_path = backup_dir / f"{name}-{timestamp}.db"
    with closing(
        sqlite3.connect(f"{source_path.as_uri()}?mode=ro", uri=True)
    ) as source:
        with closing(sqlite3.connect(backup_path)) as destination:
            source.backup(destination)
    check_integrity(backup_path)
    return backup_path


@contextmanager
def backfill_lock(lock_path):
    path = Path(lock_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("Another backfill process is already running.") from error
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


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


def main(argv=None, environ=None, opener=urlopen, stdout=None, stderr=None):
    environ = os.environ if environ is None else environ
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr
    parser = argparse.ArgumentParser(description="Incrementally import GameBlazers NFL sales")
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--pages", type=int, default=20)
    parser.add_argument("--max-new", type=int, default=200)
    parser.add_argument("--wait", type=float, default=4)
    parser.add_argument("--checkpoint")
    parser.add_argument("--start-page", type=int)
    parser.add_argument("--backfill-pages", type=int, default=1)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--backfill", action="store_true")
    actions.add_argument("--status", action="store_true")
    actions.add_argument("--set-checkpoint", type=int)
    actions.add_argument("--reset-checkpoint", action="store_true")
    actions.add_argument("--backup", action="store_true")
    actions.add_argument("--integrity-check", action="store_true")
    actions.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    db_path = Path(args.db).resolve()
    checkpoint = Path(
        args.checkpoint
        or db_path.with_name(f"{db_path.stem}.backfill.checkpoint.json")
    ).resolve()

    if args.self_test:
        self_test()
        return 0

    try:
        if args.status:
            next_page = read_checkpoint(checkpoint)
            with closing(
                sqlite3.connect(f"{db_path.as_uri()}?mode=ro", uri=True)
            ) as conn:
                total = conn.execute(
                    "SELECT COUNT(*) FROM marketplace_sales_v2"
                ).fetchone()[0]
            print(f"Checkpoint: {checkpoint}", file=stdout)
            print(f"Next page: {next_page}", file=stdout)
            print(f"marketplace_sales_v2 rows: {total}", file=stdout)
            return 0

        if args.set_checkpoint is not None:
            set_checkpoint(checkpoint, args.set_checkpoint)
            print(f"Next page set to {args.set_checkpoint}", file=stdout)
            return 0

        if args.reset_checkpoint:
            checkpoint.unlink(missing_ok=True)
            print("Checkpoint reset; next backfill page is 1", file=stdout)
            return 0

        if args.backup:
            backup = backup_database(db_path)
            print(f"Backup: {backup}", file=stdout)
            print("Backup integrity: ok", file=stdout)
            return 0

        if args.integrity_check:
            print(f"Database integrity: {check_integrity(db_path)}", file=stdout)
            return 0

        token = environ.get("GB_ACCESS_TOKEN")
        if not token:
            print(
                "Set GB_ACCESS_TOKEN for your current GameBlazers session.",
                file=stderr,
            )
            return 1

        if args.backfill:
            lock_path = checkpoint.with_suffix(".lock")
            with backfill_lock(lock_path):
                print(f"Database integrity before run: {check_integrity(db_path)}", file=stdout)
                backup_dir = db_path.parent / "backups"
                initial_backups = sorted(
                    backup_dir.glob(f"{db_path.stem}-backfill-initial-*.db")
                )
                if initial_backups:
                    check_integrity(initial_backups[-1])
                else:
                    backup = backup_database(
                        db_path, backup_dir, label="backfill-initial"
                    )
                    print(f"First-run backup: {backup}", file=stdout)
                conn = init_db(db_path)
                try:
                    result = backfill_sales(
                        conn,
                        token,
                        checkpoint,
                        start_page=args.start_page,
                        page_limit=args.backfill_pages,
                        fetcher=lambda page, access_token: fetch_sales_page(
                            page, access_token, opener=opener
                        ),
                    )
                finally:
                    conn.close()
                    print(
                        f"Database integrity after run: {check_integrity(db_path)}",
                        file=stdout,
                    )
            print(
                "Backfill: "
                f"pages={','.join(map(str, result['requested_pages']))} "
                f"returned={result['rows_returned']} "
                f"inserted={result['inserted']} "
                f"duplicates={result['duplicates']} "
                f"next_page={result['next_page']}",
                file=stdout,
            )
            return 0

        conn = init_db(db_path)
        try:
            total = update_sales(conn, token, args.pages, args.max_new, args.wait)
            print(f"Done: {total} new sales imported", file=stdout)
            return 0
        finally:
            conn.close()
    except (SalesFetchError, RuntimeError, ValueError, sqlite3.Error, OSError, KeyError) as error:
        print(f"Error: {error}", file=stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
