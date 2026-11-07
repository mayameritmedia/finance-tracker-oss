
import sqlite3
from contextlib import closing

DB_NAME = "finance.db"


def connect():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    with closing(connect()) as connection, connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL
                    CHECK(type IN ('income', 'expense')),
                description TEXT NOT NULL,
                amount_cents INTEGER NOT NULL
                    CHECK(amount_cents > 0),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        columns = [
            row[1] for row in connection.execute(
                "PRAGMA table_info(transactions)"
            )
        ]

        if "category" not in columns:
            connection.execute("""
                ALTER TABLE transactions
                ADD COLUMN category TEXT NOT NULL
                DEFAULT 'Uncategorized'
            """)


def save_transaction(kind, description, amount_cents, category):
    with closing(connect()) as connection, connection:
        connection.execute("""
            INSERT INTO transactions
                (type, description, amount_cents, category)
            VALUES (?, ?, ?, ?)
        """, (kind, description, amount_cents, category))


def get_transactions():
    with closing(connect()) as connection, connection:
        return connection.execute("""
            SELECT id, type, description,
                   amount_cents, category, created_at
            FROM transactions
            ORDER BY id DESC
        """).fetchall()


def get_monthly_transactions(month):
    with closing(connect()) as connection, connection:
        return connection.execute("""
            SELECT type, category, amount_cents
            FROM transactions
            WHERE substr(created_at, 1, 7) = ?
        """, (month,)).fetchall()


def initialize_budgets():
    with closing(connect()) as connection, connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                month TEXT NOT NULL,
                category TEXT NOT NULL,
                amount_cents INTEGER NOT NULL
                    CHECK(amount_cents >= 0),
                PRIMARY KEY (month, category)
            )
        """)


def save_budget(month, category, amount_cents):
    with closing(connect()) as connection, connection:
        connection.execute("""
            INSERT INTO budgets (month, category, amount_cents)
            VALUES (?, ?, ?)
            ON CONFLICT(month, category)
            DO UPDATE SET amount_cents = excluded.amount_cents
        """, (month, category, amount_cents))


def get_budgets(month):
    with closing(connect()) as connection, connection:
        return connection.execute("""
            SELECT category, amount_cents
            FROM budgets
            WHERE month = ?
            ORDER BY category
        """, (month,)).fetchall()


def update_transaction(
    transaction_id, description, amount_cents, category
):
    with closing(connect()) as connection, connection:
        cursor = connection.execute("""
            UPDATE transactions
            SET description = ?,
                amount_cents = ?,
                category = ?
            WHERE id = ?
        """, (
            description,
            amount_cents,
            category,
            transaction_id
        ))

        return cursor.rowcount > 0


def delete_transaction(transaction_id):
    with closing(connect()) as connection, connection:
        cursor = connection.execute("""
            DELETE FROM transactions
            WHERE id = ?
        """, (transaction_id,))

        return cursor.rowcount > 0


