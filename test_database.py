
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(
            Path(self.temp_dir.name) / "test_finance.db"
        )

        self.patcher = patch.object(
            database, "DB_NAME", self.db_path
        )
        self.patcher.start()

        database.initialize_database()
        database.initialize_budgets()

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def test_save_transaction(self):
        database.save_transaction(
            "expense", "Groceries", 2500, "Groceries"
        )

        transactions = database.get_transactions()

        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0][3], 2500)
        self.assertEqual(transactions[0][4], "Groceries")

    def test_update_transaction(self):
        database.save_transaction(
            "expense", "Food", 2000, "Groceries"
        )

        transaction_id = database.get_transactions()[0][0]

        updated = database.update_transaction(
            transaction_id, "Food Updated", 3000, "Groceries"
        )

        self.assertTrue(updated)
        self.assertEqual(
            database.get_transactions()[0][3], 3000
        )

    def test_delete_transaction(self):
        database.save_transaction(
            "expense", "Internet", 8000, "Utilities"
        )

        transaction_id = database.get_transactions()[0][0]

        deleted = database.delete_transaction(transaction_id)

        self.assertTrue(deleted)
        self.assertEqual(database.get_transactions(), [])

    def test_monthly_budget(self):
        database.save_budget(
            "2026-11", "Housing", 120000
        )

        budgets = database.get_budgets("2026-11")

        self.assertEqual(
            budgets, [("Housing", 120000)]
        )


if __name__ == "__main__":
    unittest.main()
