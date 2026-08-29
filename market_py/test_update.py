import io
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing, redirect_stdout
from pathlib import Path
from urllib.error import HTTPError, URLError
from unittest.mock import call, patch

import update


SALE = {
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
                "positions": ["WR"],
            },
        },
    },
}


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


def response(payload):
    return FakeResponse(json.dumps(payload).encode())


def http_error(code, message, headers=None):
    return HTTPError(
        "https://example.invalid", code, message, headers or {}, FakeResponse(b"")
    )


class BackfillTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.db_path = self.root / "gameblazers.db"
        self.checkpoint = self.root / "gameblazers.backfill.checkpoint.json"
        self.conn = update.init_db(self.db_path)
        self.addCleanup(self.conn.close)

    def run_backfill(self, fetcher, **kwargs):
        return update.backfill_sales(
            self.conn,
            "secret-token",
            self.checkpoint,
            fetcher=fetcher,
            **kwargs,
        )

    def test_successful_page_commits_then_advances_checkpoint_once(self):
        result = self.run_backfill(lambda page, _token: [SALE], start_page=7)

        self.assertEqual(result["requested_pages"], [7])
        self.assertEqual(result["rows_returned"], 1)
        self.assertEqual(result["inserted"], 1)
        self.assertEqual(result["duplicates"], 0)
        self.assertEqual(update.read_checkpoint(self.checkpoint), 8)
        self.assertEqual(
            self.conn.execute("SELECT COUNT(*) FROM marketplace_sales_v2").fetchone()[0],
            1,
        )

    def test_duplicate_and_same_page_rerun_are_safe(self):
        update.save_sales(self.conn, [SALE])
        first = self.run_backfill(lambda page, _token: [SALE], start_page=4)
        update.set_checkpoint(self.checkpoint, 4)
        second = self.run_backfill(lambda page, _token: [SALE])

        self.assertEqual(first["inserted"], 0)
        self.assertEqual(first["duplicates"], 1)
        self.assertEqual(second["inserted"], 0)
        self.assertEqual(second["duplicates"], 1)
        self.assertEqual(update.read_checkpoint(self.checkpoint), 5)
        self.assertEqual(
            self.conn.execute("SELECT COUNT(*) FROM marketplace_sales_v2").fetchone()[0],
            1,
        )

    def test_failures_leave_checkpoint_unchanged(self):
        failures = {
            "401": lambda _request, timeout: (_ for _ in ()).throw(
                http_error(401, "Unauthorized")
            ),
            "403": lambda _request, timeout: (_ for _ in ()).throw(
                http_error(403, "Forbidden")
            ),
            "429": lambda _request, timeout: (_ for _ in ()).throw(
                http_error(429, "Too Many Requests", {"Retry-After": "0"})
            ),
            "500": lambda _request, timeout: (_ for _ in ()).throw(
                http_error(500, "Server Error")
            ),
            "network": lambda _request, timeout: (_ for _ in ()).throw(
                URLError("offline")
            ),
            "malformed JSON": lambda _request, timeout: FakeResponse(b"not-json"),
            "unexpected object": lambda _request, timeout: response({"items": []}),
            "unexpected list member": lambda _request, timeout: response(["bad"]),
            "unexpected nested shape": lambda _request, timeout: response(
                [{"id": "bad", "marketplaceListingItemDetails": "bad"}]
            ),
        }

        for name, opener in failures.items():
            with self.subTest(name=name):
                update.set_checkpoint(self.checkpoint, 9)
                fetcher = lambda page, token, opener=opener: update.fetch_sales_page(
                    page, token, opener=opener, sleeper=lambda _seconds: None
                )
                with self.assertRaises(update.SalesFetchError):
                    self.run_backfill(fetcher)
                self.assertEqual(update.read_checkpoint(self.checkpoint), 9)
                self.assertEqual(
                    self.conn.execute(
                        "SELECT COUNT(*) FROM marketplace_sales_v2"
                    ).fetchone()[0],
                    0,
                )

    def test_page_limit_is_respected(self):
        pages = []

        def fetcher(page, _token):
            pages.append(page)
            return []

        result = self.run_backfill(fetcher, start_page=3, page_limit=2)

        self.assertEqual(pages, [3, 4])
        self.assertEqual(result["requested_pages"], [3, 4])
        self.assertEqual(update.read_checkpoint(self.checkpoint), 5)

    def test_429_honors_retry_after_before_stopping(self):
        delays = []

        with self.assertRaises(update.SalesFetchError):
            update.fetch_sales_page(
                8,
                "secret-token",
                opener=lambda _request, timeout: (_ for _ in ()).throw(
                    http_error(429, "Too Many Requests", {"Retry-After": "3"})
                ),
                sleeper=delays.append,
            )

        self.assertEqual(delays, [3.0])

    @patch("update.fetch_sales_page")
    def test_incremental_update_still_starts_at_one_and_stops_on_existing(self, fetch):
        fetch.side_effect = [[SALE], [SALE], [{**SALE, "id": "listing-2"}]]

        with redirect_stdout(io.StringIO()):
            inserted = update.update_sales(
                self.conn,
                "secret-token",
                max_pages=3,
                max_new=20,
                wait_seconds=0,
            )

        self.assertEqual(inserted, 1)
        self.assertEqual(fetch.call_args_list, [call(1, "secret-token"), call(2, "secret-token")])

    def test_status_and_checkpoint_commands_never_call_network(self):
        def fail_if_called(_request, timeout):
            self.fail("network request was attempted")

        output = io.StringIO()
        for args in (
            ["--db", str(self.db_path), "--status"],
            ["--db", str(self.db_path), "--set-checkpoint", "12"],
            ["--db", str(self.db_path), "--reset-checkpoint"],
        ):
            with self.subTest(args=args):
                self.assertEqual(
                    update.main(args, environ={}, opener=fail_if_called, stdout=output), 0
                )

    def test_cli_error_output_never_contains_access_token(self):
        token = "private-access-token"

        def unauthorized(_request, timeout):
            raise http_error(401, token)

        stdout = io.StringIO()
        stderr = io.StringIO()
        exit_code = update.main(
            ["--db", str(self.db_path), "--backfill", "--start-page", "2"],
            environ={"GB_ACCESS_TOKEN": token},
            opener=unauthorized,
            stdout=stdout,
            stderr=stderr,
        )

        logs = stdout.getvalue() + stderr.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertNotIn(token, logs)
        self.assertIn("fresh login token", logs)
        self.assertFalse(self.checkpoint.exists())

    def test_backup_is_valid_and_keeps_legacy_rows(self):
        self.conn.execute("CREATE TABLE sales_history (id INTEGER PRIMARY KEY)")
        self.conn.execute("INSERT INTO sales_history VALUES (1)")
        self.conn.commit()

        backup = update.backup_database(self.db_path, self.root / "backups")

        self.assertEqual(update.check_integrity(self.db_path), "ok")
        self.assertEqual(update.check_integrity(backup), "ok")
        with closing(sqlite3.connect(backup)) as backup_conn:
            self.assertEqual(
                backup_conn.execute("SELECT COUNT(*) FROM sales_history").fetchone()[0],
                1,
            )

    def test_first_backfill_backup_is_not_skipped_after_manual_checkpoint(self):
        update.set_checkpoint(self.checkpoint, 6)

        exit_code = update.main(
            ["--db", str(self.db_path), "--backfill"],
            environ={"GB_ACCESS_TOKEN": "secret-token"},
            opener=lambda _request, timeout: response([]),
            stdout=io.StringIO(),
            stderr=io.StringIO(),
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            len(list((self.root / "backups").glob("gameblazers-backfill-initial-*.db"))),
            1,
        )


if __name__ == "__main__":
    unittest.main()
